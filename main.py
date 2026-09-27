from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, date

from . import models, schemas, auth_utils
from .database import engine, get_db
from .services.recommendation import calculate_match

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpporTune API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- AUTH ROUTES ---
@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        name=user.name, 
        email=user.email, 
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth_utils.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth_utils.create_access_token(
        data={"sub": db_user.email, "role": db_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth_utils.get_current_user)):
    return current_user

# --- PROFILE ROUTES ---
@app.get("/api/students/profile", response_model=schemas.StudentProfileResponse)
def get_profile(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/api/students/profile", response_model=schemas.StudentProfileResponse)
def update_profile(profile_in: schemas.StudentProfileCreate, current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = models.StudentProfile(user_id=current_user.id, **profile_in.dict())
        db.add(profile)
    else:
        for key, value in profile_in.dict().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

# --- OPPORTUNITIES ROUTES ---
@app.get("/api/opportunities", response_model=list[schemas.OpportunityMatchResponse])
def get_opportunities(
    search: str = None, 
    category: str = None,
    mode: str = None,
    skills: str = None,
    min_match: int = None,
    current_user: models.User = Depends(auth_utils.get_current_user), 
    db: Session = Depends(get_db)
):
    query = db.query(models.Opportunity)
    
    if search:
        query = query.filter(models.Opportunity.title.ilike(f"%{search}%"))
    if category:
        query = query.filter(models.Opportunity.category.ilike(f"%{category}%"))
    if mode:
        query = query.filter(models.Opportunity.mode.ilike(f"%{mode}%"))
    
    opportunities = query.all()
    
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == current_user.id).first()
    
    results = []
    for opp in opportunities:
        if skills:
            # Simple skill filter
            opp_skills = (opp.required_skills or "").lower()
            if not any(s.strip().lower() in opp_skills for s in skills.split(",")):
                continue
                
        if profile:
            match_data = calculate_match(profile, opp)
            if min_match and match_data["match_score"] < min_match:
                continue
                
            opp_dict = opp.__dict__.copy()
            opp_dict.update(match_data)
            results.append(opp_dict)
        else:
            opp_dict = opp.__dict__.copy()
            opp_dict.update({
                "match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "matched_interests": [],
                "matched_category": False,
                "priority": "LOW PRIORITY",
                "days_remaining": (opp.deadline - date.today()).days if opp.deadline else None
            })
            results.append(opp_dict)
            
    # Sort by match score desc, then deadline asc
    results.sort(key=lambda x: (-x.get("match_score", 0), x.get("days_remaining", 9999) or 9999))
    return results

@app.get("/api/opportunities/{id}", response_model=schemas.OpportunityMatchResponse)
def get_opportunity(id: int, current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == current_user.id).first()
    
    opp_dict = opp.__dict__.copy()
    if profile:
        match_data = calculate_match(profile, opp)
        opp_dict.update(match_data)
    else:
        opp_dict.update({
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "matched_interests": [],
            "matched_category": False,
            "priority": "LOW PRIORITY",
            "days_remaining": (opp.deadline - date.today()).days if opp.deadline else None
        })
    return opp_dict

# --- BOOKMARKS ROUTES ---
@app.get("/api/bookmarks", response_model=list[schemas.BookmarkResponse])
def get_bookmarks(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Bookmark).filter(models.Bookmark.user_id == current_user.id).all()

@app.post("/api/bookmarks/{opportunity_id}", response_model=schemas.BookmarkResponse)
def add_bookmark(opportunity_id: int, current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.opportunity_id == opportunity_id
    ).first()
    
    if bookmark:
        return bookmark # already bookmarked
        
    bookmark = models.Bookmark(user_id=current_user.id, opportunity_id=opportunity_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark

@app.delete("/api/bookmarks/{opportunity_id}")
def delete_bookmark(opportunity_id: int, current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.opportunity_id == opportunity_id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    db.delete(bookmark)
    db.commit()
    return {"status": "success"}

# --- APPLICATIONS ROUTES ---
@app.get("/api/applications", response_model=list[schemas.ApplicationResponse])
def get_applications(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Application).filter(models.Application.user_id == current_user.id).all()

@app.put("/api/applications/{opportunity_id}/status", response_model=schemas.ApplicationResponse)
def update_application_status(
    opportunity_id: int, 
    status_update: schemas.ApplicationUpdate, 
    current_user: models.User = Depends(auth_utils.get_current_user), 
    db: Session = Depends(get_db)
):
    app = db.query(models.Application).filter(
        models.Application.user_id == current_user.id,
        models.Application.opportunity_id == opportunity_id
    ).first()
    
    if not app:
        app = models.Application(
            user_id=current_user.id, 
            opportunity_id=opportunity_id,
            status=status_update.status,
            notes=status_update.notes
        )
        db.add(app)
    else:
        app.status = status_update.status
        if status_update.notes is not None:
            app.notes = status_update.notes
            
    db.commit()
    db.refresh(app)
    return app

# --- ROADMAP ROUTES ---
@app.get("/api/roadmap", response_model=schemas.RoadmapCategoryResponse)
def get_roadmap(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == current_user.id).first()
    if not profile:
        return {"apply_now": [], "prepare_apply": [], "learn_first": []}
        
    opportunities = db.query(models.Opportunity).all()
    
    apply_now = []
    prepare_apply = []
    learn_first = []
    
    for opp in opportunities:
        match_data = calculate_match(profile, opp)
        opp_dict = opp.__dict__.copy()
        opp_dict.update(match_data)
        
        score = match_data["match_score"]
        if score >= 80 and match_data["priority"] == "HIGH PRIORITY":
            apply_now.append(opp_dict)
        elif score >= 60:
            prepare_apply.append(opp_dict)
        elif len(match_data["missing_skills"]) > 0:
            learn_first.append(opp_dict)
            
    # Sort
    apply_now.sort(key=lambda x: -x["match_score"])
    prepare_apply.sort(key=lambda x: -x["match_score"])
    learn_first.sort(key=lambda x: -x["match_score"])
    
    return {
        "apply_now": apply_now[:5],
        "prepare_apply": prepare_apply[:5],
        "learn_first": learn_first[:5]
    }

# --- ADMIN ROUTES ---
@app.post("/api/admin/opportunities", response_model=schemas.OpportunityResponse)
def create_opportunity(opp: schemas.OpportunityCreate, current_admin: models.User = Depends(auth_utils.get_current_admin), db: Session = Depends(get_db)):
    db_opp = models.Opportunity(**opp.dict())
    db.add(db_opp)
    db.commit()
    db.refresh(db_opp)
    return db_opp

@app.get("/api/admin/stats")
def get_admin_stats(current_admin: models.User = Depends(auth_utils.get_current_admin), db: Session = Depends(get_db)):
    students_count = db.query(models.User).filter(models.User.role == "student").count()
    opps_count = db.query(models.Opportunity).count()
    apps_count = db.query(models.Application).count()
    return {
        "students_count": students_count,
        "opportunities_count": opps_count,
        "applications_count": apps_count
    }

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from .models import RoleEnum, ApplicationStatusEnum

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StudentProfileBase(BaseModel):
    education: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    preferred_categories: Optional[str] = None
    preferred_mode: Optional[str] = None
    preferred_location: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OpportunityBase(BaseModel):
    title: str
    organization: str
    category: str
    description: str
    eligibility: str
    required_skills: str
    location: Optional[str] = None
    mode: Optional[str] = None
    deadline: Optional[date] = None
    benefits: Optional[str] = None
    official_url: Optional[str] = None
    image_url: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityResponse(OpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OpportunityMatchResponse(OpportunityResponse):
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    matched_interests: List[str]
    matched_category: bool
    priority: str
    days_remaining: Optional[int] = None

class BookmarkCreate(BaseModel):
    opportunity_id: int

class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    opportunity: Optional[OpportunityResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationUpdate(BaseModel):
    status: ApplicationStatusEnum
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    status: ApplicationStatusEnum
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: datetime
    opportunity: Optional[OpportunityResponse] = None
    
    class Config:
        from_attributes = True

class RoadmapCategoryResponse(BaseModel):
    apply_now: List[OpportunityMatchResponse]
    prepare_apply: List[OpportunityMatchResponse]
    learn_first: List[OpportunityMatchResponse]

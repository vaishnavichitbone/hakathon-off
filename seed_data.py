from datetime import date, timedelta
from backend.database import SessionLocal, engine
from backend import models, auth_utils

def seed_db():
    print("Initializing Database...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create Admin User
    admin = db.query(models.User).filter(models.User.email == "admin@opportune.com").first()
    if not admin:
        admin = models.User(
            name="Admin User",
            email="admin@opportune.com",
            password_hash=auth_utils.get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin)
        print("Admin user created (admin@opportune.com / admin123)")
    
    # Create Demo Student
    student = db.query(models.User).filter(models.User.email == "student@opportune.com").first()
    if not student:
        student = models.User(
            name="Alex Student",
            email="student@opportune.com",
            password_hash=auth_utils.get_password_hash("student123"),
            role="student"
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        print("Student user created (student@opportune.com / student123)")
        
        profile = models.StudentProfile(
            user_id=student.id,
            education="B.E.",
            degree="Computer Engineering",
            branch="Computer Science",
            year="Third Year",
            skills="Python, SQL, HTML, CSS, JavaScript",
            interests="AI, Software Development, Web Development",
            preferred_categories="Internships, Hackathons",
            preferred_mode="Remote, Hybrid",
            preferred_location="New York, San Francisco, Remote"
        )
        db.add(profile)
        print("Student profile created")
    
    # Check Opportunities
    if db.query(models.Opportunity).count() == 0:
        opportunities = [
            models.Opportunity(
                title="Python Developer Internship",
                organization="TechNova Solutions",
                category="Internship",
                description="Join our backend team to develop robust APIs and microservices using Python and FastAPI. Interest in Software Development is a huge plus.",
                eligibility="Pursuing B.E. or B.Tech in Computer Engineering, Third Year or Final Year",
                required_skills="Python, SQL, Git, FastAPI",
                location="Remote",
                mode="Remote",
                deadline=date.today() + timedelta(days=7),
                benefits="Stipend: $1000/month, Pre-placement offer",
                official_url="https://example.com/python-internship",
                image_url="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=500&q=80"
            ),
            models.Opportunity(
                title="Global AI Hackathon 2026",
                organization="AI Innovators",
                category="Hackathon",
                description="Build the next generation AI applications. Open to all students with interests in AI and Machine Learning.",
                eligibility="Open to all university students",
                required_skills="Python, Machine Learning, React",
                location="San Francisco, CA",
                mode="Hybrid",
                deadline=date.today() + timedelta(days=12),
                benefits="Prize pool: $50,000, Swags, Mentorship",
                official_url="https://example.com/ai-hackathon",
                image_url="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80"
            ),
            models.Opportunity(
                title="React Frontend Developer Role",
                organization="Creative Web",
                category="Internship",
                description="Seeking a UI/UX passionate student for Web Development.",
                eligibility="Computer Science students",
                required_skills="JavaScript, React, CSS, HTML",
                location="New York, NY",
                mode="On-site",
                deadline=date.today() + timedelta(days=30),
                benefits="Stipend: $1200/month",
                official_url="https://example.com/react-intern",
                image_url="https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=500&q=80"
            ),
            models.Opportunity(
                title="Google Cloud Certification Scholarship",
                organization="Cloud Gurus",
                category="Scholarship",
                description="Get 100% scholarship for Google Cloud Architect certification. Enhance your cloud and Software Development skills.",
                eligibility="Second and Third Year students",
                required_skills="SQL, Python, Cloud Computing",
                location="Remote",
                mode="Remote",
                deadline=date.today() + timedelta(days=2),
                benefits="Free Certification Voucher, Study Material",
                official_url="https://example.com/gcp-scholarship",
                image_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&q=80"
            ),
            models.Opportunity(
                title="Web Development Bootcamp",
                organization="Code Camp",
                category="Course",
                description="Master full-stack Web Development in 8 weeks.",
                eligibility="Anyone",
                required_skills="HTML, CSS",
                location="Remote",
                mode="Remote",
                deadline=date.today() + timedelta(days=45),
                benefits="Certificate of Completion",
                official_url="https://example.com/web-bootcamp",
                image_url="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&q=80"
            ),
            models.Opportunity(
                title="Data Science Winter Internship",
                organization="DataCorp",
                category="Internship",
                description="Work on big data and analytics.",
                eligibility="B.E. Computer Engineering, Final Year",
                required_skills="Python, SQL, Pandas, Machine Learning",
                location="Remote",
                mode="Remote",
                deadline=date.today() + timedelta(days=10),
                benefits="Stipend: $1500/month",
                official_url="https://example.com/data-intern",
                image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&q=80"
            ),
            models.Opportunity(
                title="UI/UX Design Competition",
                organization="Designers Hub",
                category="Competition",
                description="Design the future of mobile interfaces. Show your Web Development and UI skills.",
                eligibility="Open to all",
                required_skills="Figma, CSS",
                location="Remote",
                mode="Remote",
                deadline=date.today() + timedelta(days=3),
                benefits="Cash Prize: $2,000",
                official_url="https://example.com/design-comp",
                image_url="https://images.unsplash.com/photo-1561070791-2526d30994b5?w=500&q=80"
            ),
            models.Opportunity(
                title="Advanced Machine Learning Workshop",
                organization="AI Society",
                category="Workshop",
                description="Hands-on workshop on deep learning.",
                eligibility="Students with basic Python knowledge",
                required_skills="Python, Math",
                location="Hybrid",
                mode="Hybrid",
                deadline=date.today() + timedelta(days=20),
                benefits="Certificate, Hands-on Experience",
                official_url="https://example.com/ml-workshop",
                image_url="https://images.unsplash.com/photo-1527474305487-b87b222841cc?w=500&q=80"
            )
        ]
        
        for opp in opportunities:
            db.add(opp)
            
        db.commit()
        print(f"Added {len(opportunities)} demo opportunities.")
    else:
        print("Opportunities already exist in the database.")
        
    db.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_db()

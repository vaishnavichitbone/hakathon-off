from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class RoleEnum(str, enum.Enum):
    student = "student"
    admin = "admin"

class ApplicationStatusEnum(str, enum.Enum):
    saved = "saved"
    planning = "planning"
    applied = "applied"
    shortlisted = "shortlisted"
    rejected = "rejected"
    selected = "selected"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.student)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="user", uselist=False)
    bookmarks = relationship("Bookmark", back_populates="user")
    applications = relationship("Application", back_populates="user")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    education = Column(String)
    degree = Column(String)
    branch = Column(String)
    year = Column(String)
    skills = Column(String) 
    interests = Column(String) 
    preferred_categories = Column(String)
    preferred_mode = Column(String)
    preferred_location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    organization = Column(String)
    category = Column(String, index=True)
    description = Column(Text)
    eligibility = Column(Text)
    required_skills = Column(String)
    location = Column(String)
    mode = Column(String)
    deadline = Column(Date)
    benefits = Column(Text)
    official_url = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookmarks = relationship("Bookmark", back_populates="opportunity")
    applications = relationship("Application", back_populates="opportunity")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    opportunity = relationship("Opportunity", back_populates="bookmarks")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.saved)
    notes = Column(Text, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")

from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    top_languages = Column(JSON, nullable=True)

    
# --- ADMIN MODEL CORRECTLY ALIGNED ---
class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
# --- ADD THIS NEW JOB MODEL BELOW ---
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)              # NEW
    experience_level = Column(String, nullable=False)      # NEW
    employment_type = Column(String, nullable=False)       # NEW
    salary = Column(String, nullable=True)  
    application_link = Column(String, nullable=False)      # NEW
    description = Column(String, nullable=False)
    
    # We will store required languages as a JSON list, e.g., ["Python", "TypeScript"]
    required_languages = Column(JSON, nullable=False, default=[])
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

# --- ADD THIS NEW JOB MODEL BELOW ---
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(String, nullable=False)
    salary = Column(String, nullable=True)  # Stored as text like "$80,000 - $100,000" or an integer
    
    # We will store required languages as a JSON list, e.g., ["Python", "TypeScript"]
    required_languages = Column(JSON, nullable=False, default=[])
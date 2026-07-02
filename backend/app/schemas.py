from pydantic import BaseModel, EmailStr
from typing import List, Optional

# What we expect from the frontend on Signup
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    github_url: Optional[str] = None

# What we expect from the frontend on Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# What we send back on a successful login
class Token(BaseModel):
    access_token: str
    token_type: str
    full_name: Optional[str] = None
    
    
class JobBase(BaseModel):
    title: str
    company: str
    location: str              # NEW
    experience_level: str      # NEW
    employment_type: str       # NEW
    salary: Optional[str] = None
    application_link: str      # NEW
    description: str
    required_languages: List[str] = [] # Keep this for future logic

class JobCreate(JobBase):
    pass  # This is what an admin/company sends to create a job

class JobResponse(JobBase):
    id: int

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy database objects
        
# --- ADMIN SCHEMAS ---
class AdminCreate(BaseModel):
    email: str
    password: str
    full_name: str
    access_code: str  # The Master Key we talked about!

class AdminLogin(BaseModel):
    email: str
    password: str        
    
# --- CV STUDIO & GITHUB SYNC SCHEMAS ---

# 1. GitHub Sync Contracts
class GitHubSyncRequest(BaseModel):
    github_url: str

class JobMatchItem(BaseModel):
    title: str
    company: str
    location: str
    match_percentage: int

class GitHubSyncResponse(BaseModel):
    status: str
    username: str
    core_skills: List[str]
    job_matches: List[JobMatchItem]

# 2. AI Tailoring Contracts
class CVTailorRequest(BaseModel):
    target_job: str           # e.g., "Data analyst at Flowt"
    current_title: str        # e.g., "Backend Systems Engineer"
    current_summary: str      # The raw text from the summary box
    current_skills: str       # The raw text from the skills box
    # Optional: We can add experiences later if you want the AI to rewrite those too

class CVTailorResponse(BaseModel):
    tailored_title: str
    tailored_summary: str
    tailored_skills: str
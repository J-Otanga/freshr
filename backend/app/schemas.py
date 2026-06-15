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
    
class JobBase(BaseModel):
    title: str
    company: str
    description: str
    salary: Optional[str] = None
    required_languages: List[str] = []

class JobCreate(JobBase):
    pass  # This is what an admin/company sends to create a job

class JobResponse(JobBase):
    id: int

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy database objects
# routers/cv.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

# Create the router instance
router = APIRouter(
    prefix="/api/v1/cv",
    tags=["CV Studio"]
)

class RawCVData(BaseModel):
    title: str
    summary: str
    skills: str
    expDesc: str

class TailorRequest(BaseModel):
    job_description: str
    raw_cv: RawCVData

class TailoredCVResponse(BaseModel):
    title: str
    summary: str
    skills: str
    expDesc: str

@router.post("/tailor/", response_model=TailoredCVResponse)
async def tailor_cv_endpoint(payload: TailorRequest):
    try:
        # (Your AI prompt handling or mock data logic goes here)
        return {
            "title": "Backend Systems Engineer",
            "summary": "Results-driven Backend Developer with hands-on experience designing robust API architectures...",
            "skills": "Python, REST APIs, Node.js, Relational Databases",
            "expDesc": "Architected a full-stack task orchestration system featuring a scalable Node.js API backend..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
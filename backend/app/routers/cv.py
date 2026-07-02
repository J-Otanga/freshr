from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import our live services
from app.services.githubService import fetch_github_repositories
from app.services.AIServices import analyze_github_with_ai, generate_tailored_cv

# Create the router instance
router = APIRouter(
    prefix="/api/v1/cv",
    tags=["CV Studio"]
)

# --- INLINE SCHEMAS --- 

class RepoItem(BaseModel):
    role: str
    company: str
    desc: str

class RawCVData(BaseModel):
    title: str
    summary: str
    skills: str
    repositories: List[RepoItem]  # ✅ UPDATED: Changed from expDesc to accept array of repos

class TailorRequest(BaseModel):
    job_description: str
    raw_cv: RawCVData

class TailoredCVResponse(BaseModel):
    title: str
    summary: str
    skills: str
    best_matched_repos: List[RepoItem]  # ✅ UPDATED: Returns the top 2 chosen & rewritten repos

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

# --- ENDPOINTS ---

@router.post("/sync-github", response_model=GitHubSyncResponse)
async def sync_github_profile(payload: GitHubSyncRequest):
    try:
        # 1. Fetch live repository details asynchronously
        repos = await fetch_github_repositories(payload.github_url)
        
        # Extract username safely 
        username = payload.github_url.split("/")[-1]
        
        # 2. Run the repository list through our GPT-4o Mini analyzer
        ai_analysis = await analyze_github_with_ai(username, repos)
        
        # 3. Return the exact structure the frontend expects
        return {
            "status": "success",
            "username": username,
            "core_skills": ai_analysis.get("core_skills", []),
            "job_matches": ai_analysis.get("job_matches", [])
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub Analysis failed: {str(e)}")

@router.post("/tailor/", response_model=TailoredCVResponse)
async def tailor_cv_endpoint(payload: TailorRequest):
    try:
        # Pass the raw frontend structures cleanly to the AI Engine
        # Converting Pydantic objects to standard dictionaries for the AI handler
        raw_repos_list = [repo.dict() for repo in payload.raw_cv.repositories]
        
        tailored_data = await generate_tailored_cv(
            job_description=payload.job_description,
            raw_title=payload.raw_cv.title,
            raw_summary=payload.raw_cv.summary,
            raw_skills=payload.raw_cv.skills,
            raw_repositories=raw_repos_list  # ✅ UPDATED: Passing array of repos
        )
        
        # FastAPI automatically validates this returned dictionary against TailoredCVResponse
        return tailored_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Tailoring failed: {str(e)}")
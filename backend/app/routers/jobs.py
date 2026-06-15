from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json  # Added to safely parse data if it comes back stringified
from .. import models, schemas, database
from . import auth

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: schemas.JobCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)  # <--- THE BOUNCER
):
    new_job = models.Job(
        title=job.title,
        company=job.company,
        description=job.description,
        salary=job.salary,
        required_languages=job.required_languages
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/my-matches", response_model=List[schemas.JobResponse])
def get_my_matches(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user) # The token tells us exactly who this is!
):
    """
    Student-Facing Endpoint: Automatically fetches jobs matching the logged-in student's tech stack.
    """
    # 1. We don't need to look up the user by a URL parameter anymore. 
    # 'current_user' IS the student who sent the request!
    user_languages = set()
    if current_user.top_languages:
        raw_data = current_user.top_languages
        if isinstance(raw_data, str):
            try:
                raw_data = json.loads(raw_data)
            except Exception:
                raw_data = {}
        
        if isinstance(raw_data, dict):
            user_languages = set(raw_data.keys())
        elif isinstance(raw_data, list):
            user_languages = set(raw_data)

    # 2. Fetch all jobs to compare against
    all_jobs = db.query(models.Job).all()
    matched_jobs = []

    # 3. Match the logged-in student against the job requirements
    for job in all_jobs:
        job_reqs = set()
        if job.required_languages:
            raw_reqs = job.required_languages
            if isinstance(raw_reqs, list):
                job_reqs = set(raw_reqs)

        if job_reqs and job_reqs.issubset(user_languages):
            matched_jobs.append(job)
        elif not job_reqs:
            matched_jobs.append(job)

    return matched_jobs
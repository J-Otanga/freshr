from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.routers import adminAuth  # Import the admin authentication router

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])

# --- PROTECTED ADMIN ROUTES ---

@router.post("/", response_model=schemas.JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    # The Bouncer: Requires a valid Admin JWT token!
    current_admin: models.Admin = Depends(adminAuth.get_current_admin) 
):
    """
    Creates a new job. 
    Only verified administrators can access this endpoint.
    """
    new_job = models.Job(
        title=job.title,
        company=job.company,
        location=job.location,                  
        experience_level=job.experience_level,  
        employment_type=job.employment_type,    
        salary=job.salary,
        application_link=job.application_link,  
        description=job.description,
        required_languages=job.required_languages
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@router.put("/{job_id}", response_model=schemas.JobResponse)
def update_job(
    job_id: int, 
    updated_job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    # The Bouncer: Requires a valid Admin JWT token!
    current_admin: models.Admin = Depends(adminAuth.get_current_admin)
):
    """
    Updates an existing job.
    Only verified administrators can access this endpoint.
    """
    job_query = db.query(models.Job).filter(models.Job.id == job_id)
    job = job_query.first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} does not exist")

    # Update the job with the new data dictionary
    job_query.update(updated_job.dict(), synchronize_session=False)
    db.commit()

    return job_query.first()


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int, 
    db: Session = Depends(get_db),
    # The Bouncer: Requires a valid Admin JWT token!
    current_admin: models.Admin = Depends(adminAuth.get_current_admin)
):
    """
    Deletes a job by its ID. 
    Only verified administrators can access this endpoint.
    """
    job_query = db.query(models.Job).filter(models.Job.id == job_id)
    job = job_query.first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} does not exist")

    job_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Job successfully deleted"}


# --- PUBLIC / STUDENT ROUTES ---

@router.get("/", response_model=List[schemas.JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    """
    Fetches all active jobs.
    This is accessible to anyone (or you can add your student auth bouncer here later).
    """
    jobs = db.query(models.Job).all()
    return jobs


@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_single_job(job_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single job by its ID.
    Accessible to anyone.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} does not exist")
        
    return job
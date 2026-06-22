from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from app.services.github import get_student_languages
from app.routers import jobs, auth, adminAuth, cv 

# --- THE DATABASE RESET TRICK ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freshr Backend API")

# ✅ FIXED: Explicitly allow port 3000 instead of using "*" with credentials
# Replace your current CORS block with this one:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(adminAuth.router)

# ✅ FIXED: Explicitly adding the route prefix here ensures 
# your backend matches the frontend's 'http://localhost:8000/api/v1/cv/tailor/' call
app.include_router(cv.router) 

@app.get("/")
def root():
    return {"message": "Freshr Backend is running!"}

@app.get("/api/v1/github-test/{username}")
async def test_github_fetch(username: str):
    """
    Test endpoint to see the GitHub language fetcher in action!
    """
    languages = await get_student_languages(username)
    return {
        "github_user": username,
        "languages_found": languages
    }
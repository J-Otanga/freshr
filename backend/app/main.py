from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. ADD THIS IMPORT
from . import models
from .database import engine
from .routers import auth
from app.services.github import get_student_languages
from app.routers import jobs

# This creates the tables in PostgreSQL automatically when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freshr Backend API")

# 2. ADD THIS CORS MIDDLEWARE BLOCK
# This allows your frontend HTML pages to safely send requests to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# Plug in the Auth router we just built
app.include_router(auth.router)
app.include_router(jobs.router)

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
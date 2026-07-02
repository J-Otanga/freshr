from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from app.schemas import GitHubSyncRequest
from app.services.github import get_student_languages

# ✅ ADDED: Import the repository fetching service so profile can load live repos
from app.services.githubService import fetch_github_repositories

from app import models
from app.database import SessionLocal

# --- 1. SETUP & CONFIGURATION ---
router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI how to read the token out of the HTTP "Authorization: Bearer <TOKEN>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "your-super-secret-development-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- 2. DEPENDENCIES & SCHEMAS ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    full_name: str | None = None

# --- 3. THE BOUNCER ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token, validates it, and yields the logged-in user object.
    If the token is invalid or expired, it instantly kicks out a 401 Unauthorized error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the encrypted token using our secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        # Kick them out if the token has expired or been tampered with
        raise credentials_exception
        
    # Grab the user from the database
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user


# --- 4. THE API ROUTES ---

@router.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": new_user.email, "exp": expire}
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer", "full_name": new_user.full_name}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user.email, "exp": expire}
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt, 
        "token_type": "bearer",
        "full_name": user.full_name
    }

@router.post("/sync-github")
async def sync_github(
    request: GitHubSyncRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Takes the GitHub URL from the frontend, extracts the username,
    fetches their top languages, and saves both to the database.
    """
    username = request.github_url.strip('/').split('/')[-1]
    
    if not username:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL provided")

    try:
        languages = await get_student_languages(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch GitHub data: {str(e)}")

    current_user.github_url = request.github_url
    current_user.top_languages = languages
    
    db.commit()
    db.refresh(current_user)

    return {
        "status": "success",
        "username": username,
        "core_skills": current_user.top_languages
    }
    
@router.get("/profile")
async def get_profile(current_user: models.User = Depends(get_current_user)):
    """
    Securely returns the logged-in user's database profile and dynamically 
    fetches live repository details if they have a GitHub URL synced.
    """
    # ✅ UPDATED: Fetch repositories dynamically on the fly if a URL exists
    live_repos = []
    if current_user.github_url:
        try:
            live_repos = await fetch_github_repositories(current_user.github_url)
        except Exception as e:
            # Fallback gracefully to an empty list if the live GitHub fetch hits a rate limit or network issue
            print(f"Graceful fallback: Failed to dynamically stream profile repos: {e}")
            live_repos = []

    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "github_url": current_user.github_url,
        "core_skills": current_user.top_languages,
        "repos": live_repos  # ✅ Return real live repos with URLs to the frontend!
    }
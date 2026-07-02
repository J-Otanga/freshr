from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import os

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/admin/auth", tags=["Admin Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/auth/login")

SECRET_KEY = "your-super-secret-development-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

super_secret_master_code = "FRESHR-ADMIN-2026"

# --- THE ADMIN BOUNCER ---
def get_current_admin(token: str = Depends(admin_oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token to verify an ADMIN.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    admin = db.query(models.Admin).filter(models.Admin.email == email).first()
    if admin is None:
        raise credentials_exception
        
    return admin

# --- ADMIN ROUTES ---
@router.post("/register")
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    # 1. Check Master Key
    if admin.access_code != super_secret_master_code:
        raise HTTPException(status_code=403, detail="Invalid Platform Access Code")

    # 2. Check if admin exists
    existing_admin = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    # 3. Hash and save
    hashed_pw = pwd_context.hash(admin.password)
    new_admin = models.Admin(email=admin.email, password_hash=hashed_pw, full_name=admin.full_name)
    
    db.add(new_admin)
    db.commit()
    return {"message": "Admin account created successfully"}

@router.post("/login", response_model=schemas.Token)
def login_admin(admin_data: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == admin_data.email).first()
    
    if not admin or not pwd_context.verify(admin_data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": admin.email, "exp": expire, "role": "admin"}
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer"}
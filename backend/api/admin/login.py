import jwt
import os
from fastapi import HTTPException, status, Depends
from db.models import Admin, Config
from db.get_db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize the password hasher
ph = PasswordHasher()

# Secret key to encode the JWT token (you should store it securely in an environment variable)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expires in 30 minutes

# Define Pydantic model for the request body
class LoginRequest(BaseModel):
    email: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Fetch the admin by email
    admin = db.query(Admin).filter(Admin.email == login_data.email).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Check if the admin is approved
    if not admin.approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin is not approved")

    # Fetch the max_login_attempts from the Config table
    max_login_attempts = db.query(Config).filter(Config.key == 'max_login_attempts').first()
    if not max_login_attempts:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Max login attempts configuration not found")
    
    max_login_attempts = int(max_login_attempts.value)  # Convert to integer

    # Manually verify the password with the stored hash
    try:
        if ph.verify(admin.password_hash, login_data.password):
            print(f"Password for {login_data.email} verified successfully!")
            
            # Create access token upon successful login
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(admin.id)}, expires_delta=access_token_expires  # Convert admin.id to string
            )
            return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
        else:
            print(f"Password verification failed for: {login_data.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except Exception as e:
        print(f"Error during password verification: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

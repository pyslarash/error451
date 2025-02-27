from fastapi import HTTPException, Depends, Header
from db.models import Admin, BlacklistedToken
from db.get_db import get_db
from sqlalchemy.orm import Session
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def get_current_admin(db: Session = Depends(get_db), authorization: str = Header(None)):
    try:
        # Check if the Authorization header is provided
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer token is missing or invalid")
        
        # Extract the token from the Authorization header
        token = authorization.split(" ")[1]
        print(f"Received Token for Validation: {token}")  # Debugging line for token
        
        # Check if the token is blacklisted
        blacklisted_token = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if blacklisted_token:
            raise HTTPException(status_code=401, detail="Token is blacklisted")

        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Decoded Payload in get_current_admin: {payload}")  # Debugging line for decoded token
        
        admin_id = payload.get("sub")  # This is the admin ID
        if admin_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Query the admin by id (NOT email)
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError as e:
        print(f"Error decoding token: {e}")  # Debugging line for errors
        raise HTTPException(status_code=401, detail="Invalid token")

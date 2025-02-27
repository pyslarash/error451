import os
from fastapi import Depends, Request, HTTPException, status
from db.get_db import get_db
from sqlalchemy.orm import Session
from db.models import BlacklistedToken
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Dependency to check token validity and blacklist
def check_token(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing")
    
    try:
        # Extract the actual token from the Authorization header
        token = token.split(" ")[1]  # Bearer <token>
        
        # Check if the token is blacklisted
        blacklisted_token = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if blacklisted_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted")
        
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Pass the payload to the route handler
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

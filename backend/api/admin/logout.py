from fastapi import HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from db.models import BlacklistedToken
from db.get_db import get_db
from sqlalchemy.orm import Session
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Token blacklisting function
def logout_admin(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    
    if token is None or not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing or invalid format")
    
    token = token.split(" ")[1]  # Extract the token from the "Bearer <token>" format
    print(f"Received Token for Logout: {token}")  # Debugging line for token received

    try:
        # Verify and decode the token to get the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded Payload: {payload}")  # Debugging line for decoded token
        
        # Check if the token is already blacklisted
        existing_token = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if existing_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This admin already logged out")
        
        # Add the token to the blacklist table
        db.add(BlacklistedToken(token=token))  # Add the token to the blacklist table
        db.commit()
        
        return JSONResponse({"message": "Logout successful"}, status_code=status.HTTP_200_OK)
    
    except jwt.ExpiredSignatureError:
        print("Token expired!")  # Debugging line for expired token
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is already expired")
    except jwt.PyJWTError:
        print("Invalid token!")  # Debugging line for invalid token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

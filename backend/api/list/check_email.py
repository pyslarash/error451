from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from db.get_db import get_db  # Assuming you already have the get_db function
from db.models import List  # Assuming you already have the List model
from pydantic import BaseModel

# Pydantic model to accept the request body with email
class CheckEmailRequest(BaseModel):
    email: str

# Function to check if the email already exists in the List
def check_email(request: CheckEmailRequest, db: Session = Depends(get_db)) -> bool:
    email = request.email  # Extract the email from the request object
    
    # Check if the email exists in the List table
    existing_email = db.query(List).filter(List.email == email).first()
    
    # If email exists, raise an exception with a relevant error message
    if existing_email:
        raise HTTPException(status_code=400, detail="You've used this email before")
    
    # If email doesn't exist, return False
    return False
import random
import string
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.list.send_confirmation_email import send_confirmation_email
from db.get_db import get_db  # Assuming you already have the `get_db` function
from db.models import List  # Assuming you already have the List model
from datetime import datetime, timedelta  # Fix: Import timedelta correctly

app = FastAPI()

# Function to generate a unique 10-character referral code
def generate_referral_code(db: Session) -> str:
    while True:
        # Generate a random 10-character alphanumeric code
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Check if the code already exists in the database
        existing_code = db.query(List).filter(List.referral_code == code).first()
        
        if not existing_code:
            return code  # Return the unique code if not found in the database

# Pydantic model to validate and parse the incoming JSON data
class ListRequest(BaseModel):
    name: str
    email: str
    country_code: str  # Country code, should be two-letter code like 'US', 'RU', etc.
    city: str
    state_code: str = None  # Optional, needed if country is 'US'
    zip: str = None  # Optional, needed if country is 'US'
    subscribed: bool = True  # Default to True

    class Config:
        orm_mode = True

# Function to add a new record to the List table
@app.post("/add-to-list")
def add_to_list(
    list_data: ListRequest,  # Expect the request body as the ListRequest Pydantic model
    db: Session = Depends(get_db)  # Dependency to get the database session
):
    # Validate country code and ensure it's "US" if state_code and zip are provided
    if list_data.country_code.lower() == "us":
        if not list_data.state_code or not list_data.zip:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="For US addresses, state code and zip are required")
    else:
        # If it's not US, make sure state_code and zip are not provided
        if list_data.state_code or list_data.zip:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State and zip should only be provided for US addresses")
    
    # Check if email already exists in the database
    existing_email = db.query(List).filter(List.email == list_data.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists in the list")
    
    # Generate a unique referral code
    referral_code = generate_referral_code(db)
    
    # Create a new List entry
    new_entry = List(
        name=list_data.name,
        email=list_data.email,
        country_code=list_data.country_code,
        city=list_data.city,
        state_code=list_data.state_code,
        zip=list_data.zip,
        referral_code=referral_code,
        confirmed=False,  # Default to False
        subscribed=list_data.subscribed  # Set the subscription status
    )
    
    # Add the new entry to the database
    db.add(new_entry)
    try:
        db.commit()  # Commit the transaction to the database
    except IntegrityError:
        db.rollback()  # Rollback in case of an integrity error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while saving the data")
    
    db.refresh(new_entry)
    
    # Send confirmation email with referral code
    send_confirmation_email(list_data.email, referral_code)  # Corrected to use list_data.email
    
    db.refresh(new_entry)  # Refresh the instance to reflect changes
    return {"message": "Record added successfully", "referral_code": referral_code}

from db.models import Admin
from db.get_db import get_db  # Correct import for get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from argon2 import PasswordHasher

# Initialize the password hasher
ph = PasswordHasher()

# Pydantic model for the input data
class AdminCreate(BaseModel):
    email: str
    password: str  # Only the plain password is needed
    two_factor: bool = False

def create_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_admin = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Set the approved status based on the number of existing admins
    existing_admins = db.query(Admin).count()
    approved_status = True if existing_admins == 0 else False

    # Create a new admin with the correct approved value
    new_admin = Admin(
        email=admin_data.email,
        password_hash=admin_data.password,  # Hash the password here using the hasher
        two_factor=admin_data.two_factor,
        approved=approved_status  # Set the approved value
    )

    # Add and commit the new admin to the database
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"message": "Admin created successfully"}

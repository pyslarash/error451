from fastapi import HTTPException, status, Depends
from db.models import Admin
from db.get_db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from argon2 import PasswordHasher
from api.admin.get_current_admin import get_current_admin  # Function to get current admin from token

# Initialize the password hasher
ph = PasswordHasher()

# Pydantic model for the input data
class AdminUpdate(BaseModel):
    email: str = None
    password: str = None  # Password is optional
    approved: bool = None  # Will be ignored for self-update

def edit_other_admin(
    admin_id: int,  # Now we accept the admin_id as a path parameter
    admin_data: AdminUpdate, 
    current_admin: Admin = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    # Fetch the admin to be edited using the admin_id passed in the URL
    admin_to_edit = db.query(Admin).filter(Admin.id == admin_id).first()
    
    if not admin_to_edit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # Check if the current admin is trying to edit their own account or another admin's account
    if current_admin.id == admin_to_edit.id:
        # Prevent editing their own account
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot edit your own account")

    # Check if the new email already exists in the database under another admin account
    if admin_data.email:
        existing_admin_with_email = db.query(Admin).filter(Admin.email == admin_data.email).first()
        if existing_admin_with_email and existing_admin_with_email.id != admin_to_edit.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists under another account")

    # Allow editing of email, password, and approved status for other admins
    if admin_data.email:
        admin_to_edit.email = admin_data.email

    if admin_data.password:
        admin_to_edit.password_hash = admin_data.password

    if admin_data.approved is not None:
        # Allow editing approved status for another admin
        admin_to_edit.approved = admin_data.approved

    # Commit the changes to the database
    db.commit()
    db.refresh(admin_to_edit)

    return {"message": "Admin updated successfully"}

from fastapi import HTTPException, status, Depends
from db.models import Admin
from db.get_db import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from api.admin.get_current_admin import get_current_admin  # Function to get current admin from token

# Pydantic model for the input data
class AdminUpdate(BaseModel):
    email: str = None
    password: str = None  # Password is optional
    two_factor: bool = None
    approved: bool = None  # Will be ignored for self-update

def edit_admin(admin_data: AdminUpdate, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Fetch the current admin using the id from the token (current_admin)
    print(f"Editing admin: {current_admin.id}")  # Debugging line to verify current admin ID
    admin = db.query(Admin).filter(Admin.id == current_admin.id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # Check if the current admin is trying to edit their own account or another admin's account
    if current_admin.id == admin.id:
        # Allow editing email, password, and two_factor for their own account but not approved
        if admin_data.email:
            print(f"Changing email to: {admin_data.email}")  # Debugging line for email change
            admin.email = admin_data.email
        if admin_data.password:
            print(f"Changing password for admin {admin.id}")  # Debugging line for password change
            admin.password_hash = admin_data.password  # Don't hash the password again
        if admin_data.two_factor is not None:
            print(f"Changing two_factor to: {admin_data.two_factor}")  # Debugging line for two_factor change
            admin.two_factor = admin_data.two_factor
        
        # Prevent changing the 'approved' status for their own account
        if admin_data.approved is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to change your own approval status")
    
    else:
        # Allow editing approved status for another admin
        if admin_data.approved is not None:
            print(f"Changing approved status to: {admin_data.approved}")  # Debugging line for approved status change
            admin.approved = admin_data.approved
        
        # Prevent editing of other fields if not the current admin's account
        if admin_data.email or admin_data.password or admin_data.two_factor is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to edit this admin's information")

    # Commit the changes to the database
    db.commit()
    db.refresh(admin)

    return {"message": "Admin updated successfully"}

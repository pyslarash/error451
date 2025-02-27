from fastapi import HTTPException, Depends
from db.models import Admin
from db.get_db import get_db
from sqlalchemy.orm import Session
from api.admin.get_current_admin import get_current_admin  # Function to get current admin from token

def get_admin(current_admin: Admin = Depends(get_current_admin)):
    # Return only the admin's email, two_factor, and approved status
    return {
        "email": current_admin.email,
        "two_factor": current_admin.two_factor,
        "approved": current_admin.approved
    }

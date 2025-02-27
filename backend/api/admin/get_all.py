from fastapi import HTTPException, Depends
from db.models import Admin
from db.get_db import get_db
from sqlalchemy.orm import Session
from api.admin.get_current_admin import get_current_admin  # Function to get current admin from token
from pydantic import BaseModel
from typing import List

# Pydantic model for response
class AdminInfo(BaseModel):
    id: int
    email: str
    approved: bool

    class Config:
        orm_mode = True

def get_admins(current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)) -> List[AdminInfo]:
    # Fetch all admins except the current admin
    admins = db.query(Admin).filter(Admin.id != current_admin.id).all()
    
    if not admins:
        raise HTTPException(status_code=404, detail="No other admins found")
    
    # Return the admins excluding the current admin, with their id, email, and approved status
    return [AdminInfo(id=admin.id, email=admin.email, approved=admin.approved) for admin in admins]

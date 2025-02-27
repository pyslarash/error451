from fastapi import APIRouter

# Create a new router for the beep endpoint
router = APIRouter()

@router.get("/beep")
def beep():
    return {"message": "boop"}
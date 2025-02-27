from fastapi import APIRouter
from api.admin import router as admin_router  # Import the admin router
from api.beep import router as beep_router  # Import the beep router

router = APIRouter()

# Include the admin and beep routers
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
router.include_router(beep_router, prefix="/api", tags=["Beep"])

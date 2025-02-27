from fastapi import APIRouter
from api.admin import router as admin_router  # Import the admin router
from api.beep import router as beep_router  # Import the beep router
from api.list import router as list_router
from api.list.send_confirmation_email import confirm_email, resend_link, download_file

router = APIRouter()

# Include the admin and beep routers
router.include_router(beep_router, prefix="/api", tags=["Beep"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
router.include_router(list_router, prefix="/list", tags=["List"])

# Dealing with links in emails
router.add_api_route("/{referral_code}", confirm_email, methods=["GET"])
router.add_api_route("/lost/{referral_code}", resend_link, methods=["GET"])
router.add_api_route("/download/{download_token}", download_file, methods=["GET"])
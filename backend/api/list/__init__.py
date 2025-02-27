from fastapi import APIRouter
from api.list.add import add_to_list
from api.list.check_email import check_email

router = APIRouter()

# Add login and create routes to the admin router
router.add_api_route("/add", add_to_list, methods=["POST"])
router.add_api_route("/check-email", check_email, methods=["POST"])

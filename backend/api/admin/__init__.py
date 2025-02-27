from fastapi import APIRouter
from api.admin.login import login_user  # Import login logic
from api.admin.create import create_admin  # Import create logic
from api.admin.logout import logout_admin
from api.admin.edit import edit_admin
from api.admin.get import get_admin
from api.admin.get_all import get_admins
from api.admin.edit_other import edit_other_admin
router = APIRouter()

# Add login and create routes to the admin router
router.add_api_route("/login", login_user, methods=["POST"])
router.add_api_route("/create", create_admin, methods=["POST"])
router.add_api_route("/logout", logout_admin, methods=["POST"])
router.add_api_route("/edit", edit_admin, methods=["PUT"])
router.add_api_route("/get", get_admin, methods=["GET"])
router.add_api_route("/get-all", get_admins, methods=["GET"])
router.add_api_route("/edit-other/{admin_id}", edit_other_admin, methods=["PUT"])
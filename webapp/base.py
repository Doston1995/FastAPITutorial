from webapp.jobs import route_jobs
from webapp.users import route_users
from webapp.auth import route_login
from fastapi import APIRouter


web_app_router = APIRouter()
web_app_router.include_router(route_jobs.router, prefix="", tags=["job-webapp"])
web_app_router.include_router(route_users.router, prefix="", tags=["users-webapp"]) 
web_app_router.include_router(route_login.router, prefix="", tags=["auth-webapp"]) 
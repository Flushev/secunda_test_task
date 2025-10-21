from fastapi import APIRouter, Depends

from app.security.api_key import require_api_key
from .organizations import router as organizations_router
from .activities import router as activities_router
from .buildings import router as buildings_router


api_v1_router = APIRouter(dependencies=[Depends(require_api_key)])
api_v1_router.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])
api_v1_router.include_router(activities_router, prefix="/activities", tags=["Activities"])
api_v1_router.include_router(buildings_router, prefix="/buildings", tags=["Buildings"])

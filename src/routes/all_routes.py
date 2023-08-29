from fastapi import APIRouter
from src.routes.backup import router as backup_router

router = APIRouter()


router.include_router(backup_router)

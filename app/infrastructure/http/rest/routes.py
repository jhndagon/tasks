from fastapi import APIRouter

from app.infrastructure.http.rest.controllers.system_controller import router as system_router
from app.infrastructure.http.rest.controllers.task_controller import router as task_router

router = APIRouter()
router.include_router(system_router)
router.include_router(task_router)

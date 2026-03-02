from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Tasks API is running"}


@router.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

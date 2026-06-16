from fastapi import APIRouter

from app.infrastructure.observability.metrics import metrics_response

router = APIRouter(tags=["system"])


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Tasks API is running"}


@router.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


router.add_api_route(
    "/metrics",
    metrics_response,
    methods=["GET"],
    include_in_schema=False,
)

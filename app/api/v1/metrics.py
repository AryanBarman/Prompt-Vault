from app.core.metrics import metrics
from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Get system metrics")
def get_metrics():
    return {
        "total_requests": metrics.total_requests,
        "total_errors": metrics.total_errors,
        "total_domain_errors": metrics.total_domain_errors,
        "total_internal_errors": metrics.total_internal_errors,
        "average_response_time_ms": metrics.average_response_time,
    }
"""Cross-cutting views (health check)."""
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    tags=["Système"],
    summary="Vérifier que le service tourne",
    responses={200: {"type": "object", "example": {"status": "ok", "service": "trustline"}}},
)
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])  # health check must never be rate-limited
def health(request):
    """Simple liveness endpoint used by the front-ends and monitoring."""
    return Response(
        {
            "status": "ok",
            "service": "trustline",
            "time": timezone.now().isoformat(),
        }
    )

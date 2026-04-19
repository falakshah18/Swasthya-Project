"""
Clean v2 API views — no auth required for frontend use.
These are thin wrappers; all logic lives in views.py / services.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json

from .views import (
    _build_ai_reply, _load_facilities, _localized_facility, TYPE_LABELS
)


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok", "version": "2.0"})

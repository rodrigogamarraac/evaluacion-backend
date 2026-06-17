from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path


def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "service": "django", "dependencies": {"postgres": "ok"}})
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "service": "django", "dependencies": {"postgres": "error"}, "detail": str(exc)},
            status=503,
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
]

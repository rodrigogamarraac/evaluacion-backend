from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def healthz(request):
    return JsonResponse({
        "status": "ok",
        "service": "django"
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
]
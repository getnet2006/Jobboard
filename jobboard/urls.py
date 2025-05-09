"""
URL configuration for jobboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter
from jobs.views import ApplicationViewSet, ReviewViewSet

router = DefaultRouter()
router.register("applications", ApplicationViewSet)
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Schema generation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Optional: ReDoc alternative UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/", include("accounts.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/", include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

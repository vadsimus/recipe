"""
URL configuration for recipe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from recipe_app.views import (
    CurrentUserView,
    IngredientListCreateView,
    RecipeListCreateView,
    RecipeDetailView,
    RecipeImageUploadView,
    UserRegistrationView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ingredient endpoints
    path('api/ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    # Recipe endpoints
    path('api/recipes/', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('api/recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('api/recipes/<int:pk>/upload-image/', RecipeImageUploadView.as_view(), name='recipe-upload-image'),
    # User registration
    path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # DRF-Spectacular endpoints for schema and interactive docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/currentUser/', CurrentUserView.as_view(), name='current-user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLConf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from apps.users.tokens.views import (LoginCheckView, TokenObtainPairView,
                                     TokenRefreshView, TokenVerifyView)
from apps.users.views import OAuthRegistrationView
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from main import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response


class HealthCheckView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: ''})
    def get(self, request):
        return Response(data='OK', status=status.HTTP_200_OK)


urlpatterns = \
    [
        # Admin panel
        path('admin/', admin.site.urls),

        # Health check http server
        path('health', HealthCheckView.as_view(), name='health_check'),
        path('__debug__/', include('debug_toolbar.urls')),

        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

        # Web API Authentication
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('token/check/', LoginCheckView.as_view(), name='token_check_auth'),
        path('token/social', OAuthRegistrationView.as_view(), name='token_obtain_pair_by_social'),
        # path('social/', include('social_django.urls', namespace='social')),

        path('api/v1/users/', include('apps.users.urls', namespace='users')),
        path('api/v1/import/', include('apps.importer.urls', namespace='importer')),
        path('api/v1/events/', include('apps.events.urls', namespace='events')),

    ] + static(settings.MEDIA_PATH, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

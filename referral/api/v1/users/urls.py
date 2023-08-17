from api.utils import OptionalSlashRouter
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from . import views

v10 = OptionalSlashRouter()
v10.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(v10.urls)),
    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    )
]

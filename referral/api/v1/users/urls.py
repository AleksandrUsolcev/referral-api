from api.utils import OptionalSlashRouter
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from . import views

v10 = OptionalSlashRouter()
v10.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(v10.urls)),
    re_path(
        r'^auth/send_code/?$',
        views.PhoneSendCodeView.as_view(),
        name='send_code'
    ),
    re_path(
        r'^auth/jwt/get_by_phone/?$',
        views.PhoneTokenView.as_view(),
        name='jwt_get_by_phone'
    ),
    re_path(
        r'^schema/?$',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    re_path(
        r'^redoc/?$',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    )
]

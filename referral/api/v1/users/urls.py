from api.utils import OptionalSlashRouter
from django.urls import include, path

from . import views

v10 = OptionalSlashRouter()
v10.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(v10.urls)),
]

from api.v1.users import urls as urls_users
from django.urls import include, path

urlpatterns = [
    path('', include(urls_users)),
]

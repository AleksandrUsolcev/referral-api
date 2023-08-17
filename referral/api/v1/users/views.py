from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('email', 'first_name', 'last_name',
                     'phone', 'invite_code', 'invited_by_code')
    filterset_fields = ('email', 'first_name', 'last_name',
                        'phone', 'invite_code', 'invited_by_code')
    http_method_names = ('get', 'patch')

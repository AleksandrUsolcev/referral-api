import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import (TokenRefreshSerializer,
                                                  TokenVerifySerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.models import AuthCode

from .serializers import (PhoneSendCodeSerializer, PhoneTokenSerializer,
                          UserDetailsSerializer, UserSerializer,
                          UserUpdateSerializer)

User = get_user_model()


@extend_schema(tags=['Users'])
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('email', 'first_name', 'last_name',
                     'phone', 'invite_code', 'invited_by_code')
    filterset_fields = ('email', 'first_name', 'last_name',
                        'phone', 'invite_code', 'invited_by_code')
    http_method_names = ('get',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailsSerializer
        return UserSerializer

    @extend_schema(
        summary='Список пользователей',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Информация о пользователе',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['Users'])
class CurrentUserView(APIView):

    @extend_schema(
        summary='Текущий пользователь',
        description='Возвращает текущего пользователя',
        responses={200: UserDetailsSerializer}
    )
    def get(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary='Текущий пользователь',
        description='Изменение текущего пользователя',
        request=UserUpdateSerializer,
        responses={200: UserDetailsSerializer}
    )
    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class PhoneSendCodeView(APIView):

    permission_classes = (AllowAny,)
    serializer_class = PhoneSendCodeSerializer

    @extend_schema(
        summary='Прислать код на номер телефона',
        description=(
            'Присваивает указанному номеру телефона 4-х значный код и '
            'возвращает его в ответе.'
        ),
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='code',
                fields={'code': serializers.IntegerField()}
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data.get('phone')
        auth_code = random.randint(1000, 9999)
        hashed_code = make_password(str(auth_code), salt=None)

        AuthCode.objects.update_or_create(
            phone=phone,
            defaults={
                'code': hashed_code,
                'created': timezone.now()
            }
        )
        # тут может быть функция с отправкой СМС с кодом через сторонний сервис
        return Response({'code': auth_code}, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class PhoneTokenView(APIView):

    permission_classes = (AllowAny,)
    serializer_class = PhoneTokenSerializer

    @extend_schema(
        summary='Получение токенов по номеру телефона и коду',
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='tokens',
                fields={
                    'access': serializers.CharField(),
                    'refresh': serializers.CharField()
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data.get('phone')
        code = serializer.validated_data.get('code')
        invited_by_code = serializer.validated_data.get('invited_by_code')

        auth_code = AuthCode.objects.filter(phone=phone).first()

        if not auth_code or not check_password(code, auth_code.code):
            return Response(
                {'code': 'Неверный код.'},
                status=status.HTTP_403_FORBIDDEN
            )
        difference = timezone.now() - auth_code.created
        time_expires = int(settings.AUTH_CODE_EXPIRES_MINUTES)
        if difference > timezone.timedelta(minutes=time_expires):
            return Response(
                {'code': 'Время действия кода истекло.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_data = {'invited_by_code': None}

        if invited_by_code:
            user = User.objects.filter(invite_code__iexact=invited_by_code)
            if not user.exists():
                return Response(
                    {'invited_by_code': 'Неверный реферальный код.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            ref_user = user.first()
            if (
                ref_user.phone == phone
                and ref_user.invite_code.lower() == invited_by_code.lower()
            ):
                return Response(
                    {'invited_by_code': 'Нельзя использовать свой код.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            user_data['invited_by_code'] = invited_by_code

        user, _ = User.objects.update_or_create(
            phone=phone,
            defaults=user_data
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        auth_code.delete()
        return Response(
            {'access': access_token, 'refresh': str(refresh)},
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['Auth'])
class TokenRefreshView(TokenRefreshView):

    serializer_class = TokenRefreshSerializer

    @extend_schema(
        summary='Рефреш токена',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Auth'])
class TokenVerifyView(TokenVerifyView):

    serializer_class = TokenVerifySerializer

    @extend_schema(
        summary='Проверка токена',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

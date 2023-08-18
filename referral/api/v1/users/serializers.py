from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class InvitedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser')


class UserDetailsSerializer(UserSerializer):

    invited = serializers.SerializerMethodField()

    @extend_schema_field(InvitedUserSerializer(many=True))
    def get_invited(self, obj):
        invited_users = User.objects.filter(
            invited_by_code__iexact=obj.invite_code
        )
        invited_serializer = InvitedUserSerializer(invited_users, many=True)
        return invited_serializer.data


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'invited_by_code', 'email')

    def validate_invited_by_code(self, value):
        user = self.instance

        if value == user.invite_code:
            raise serializers.ValidationError('Нельзя использовать свой код.')

        try:
            User.objects.get(invite_code__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Пользователь с таким кодом не найден.'
            )

        return value

    def to_representation(self, instance):
        return UserDetailsSerializer(instance, context=self.context).data


class PhoneSendCodeSerializer(serializers.Serializer):

    phone = PhoneNumberField()

    class Meta:
        fields = ('phone',)


class PhoneTokenSerializer(serializers.Serializer):

    phone = PhoneNumberField()
    code = serializers.IntegerField()
    invited_by_code = serializers.CharField(required=False)

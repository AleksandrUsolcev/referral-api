from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser')


class PhoneSendCodeSerializer(serializers.Serializer):

    phone = PhoneNumberField()

    class Meta:
        fields = ('phone',)


class PhoneTokenSerializer(serializers.Serializer):

    phone = PhoneNumberField()
    code = serializers.IntegerField()
    invited_by_code = serializers.CharField(required=False)

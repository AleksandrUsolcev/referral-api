from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import AuthCode, User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = super(UserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError('Fill out both fields')
        return password2


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'phone', 'invite_code', 'date_joined')
    ordering = ('date_joined',)
    fieldsets = (
        (
            ('Основная информация'),
            {'fields': ('email', 'phone', 'invite_code', 'invited_by_code',
                        'first_name', 'last_name', 'password')}
        ),
        (
            ('Роли и права'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (
            ('Даты'),
            {'fields': ('last_login', 'date_joined')}
        ),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': (
        'phone', 'invited_by_code', 'email', 'first_name', 'last_name',
        'password1', 'password2'
    ), }), )
    readonly_fields = ('invite_code',)


@admin.register(AuthCode)
class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created', 'expire_date')
    readonly_fields = ('phone', 'created', 'expire_date')
    exclude = ('code',)
    ordering = ('-created',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

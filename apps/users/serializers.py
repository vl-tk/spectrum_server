from apps.users.errors import (EmailDoesNotExist, PasswordsDoNotMatch,
                               ResetCodeOrEmailInvalid)
from apps.users.models import User
from apps.users.redis import NewMailCache
from apps.users.services.user import UserService
# from apps.users.signals import S_new_password_created
from apps.users.tokens.serializers import TokenObtainPairSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(**kwargs)


class EmailField(serializers.EmailField):
    def __init__(self, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'email'

        super().__init__(**kwargs)


class CodeField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('style', {})

        super().__init__(**kwargs)


class UserRegisterSerializer(serializers.ModelSerializer):

    email = EmailField(required=True)
    first_name = CharField(required=False, allow_blank=True)
    last_name = CharField(required=False, allow_blank=True)
    password = PasswordField(required=False, write_only=True, min_length=1)

    user_for_order_created = False
    user_uuid = None

    class Meta:
        model = User
        fields = [
            'pk',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        read_only_fields = ['pk']

    def validate(self, attrs):

        try:
            User.objects.all().get_by_email(attrs['email'])
            raise ValidationError({'email': 'User already exists.'})
        except User.DoesNotExist:
            pass

        # case: if we autocreate password for user registration during order placement
        self.user_uuid = self.context['request'].COOKIES.get('user_uuid')

        if not attrs.get('password'):

            if not self.user_uuid:
                raise ValidationError({'password': 'Password is required'})

            elif self.user_uuid:

                if self._can_be_registered_without_password():
                    attrs['password'] = UserService().make_random_password()
                else:
                    raise ValidationError({'user_uuid': 'User uuid is not valid'})

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            is_email_active=bool(self.user_uuid)
        )

        # S_new_password_created.send(
        #     sender=User,
        #     instance=user,
        #     new_password=validated_data.get('password'),
        # )

        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if self.user_for_order_created:
            refresh = TokenObtainPairSerializer.get_token(instance)
            ret['refresh'] = str(refresh)
            ret['access'] = str(refresh.access_token)

        return ret


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used only when customer edits his profile
    """

    email = CharField(required=True, allow_blank=False)
    first_name = CharField(required=True, allow_blank=False)
    last_name = CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'pk',
            'first_name',
            'last_name',
            'email',
            'avatar',
        ]
        read_only_fields = ['pk']


class ChangePasswordSerializer(serializers.Serializer):
    password = PasswordField()
    new_password = PasswordField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        super().validate(attrs)
        if not self.context['request'].user.check_password(attrs.get('password')):
            raise PasswordsDoNotMatch({
                'password': 'Wrong password'
            })
        return {'password': attrs.get('new_password')}

    def set_password(self):
        UserService.set_password(
            self.context['request'].user, self.validated_data.get('password'))


class RequestResetPasswordSerializer(serializers.Serializer):
    email = EmailField()
    user = None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            email = attrs.get('email').lower()
            self.user = User.objects.all().get_by_email(attrs['email'])
        except User.DoesNotExist:
            raise EmailDoesNotExist()
        return {'email': email}

    def send_make_new_password(self):
        UserService().send_make_new_password(self.user)


class ConfirmEmailSerializer(serializers.Serializer):
    code = CodeField(write_only=True)
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)
    user = None

    class Meta:
        fields = ['code', 'access', 'refresh']
        read_only_fields = ['access', 'refresh']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            self.user = User.objects.all().get_by_activation_code(attrs.get('code'))
        except User.DoesNotExist:
            raise ValidationError({'code': 'Not found'})
        return super().validate(attrs)

    def confirm_email(self):
        UserService.confirm_email(self.user)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        refresh = TokenObtainPairSerializer.get_token(self.user)
        ret['refresh'] = str(refresh)
        ret['access'] = str(refresh.access_token)
        return ret


class RequestChangeEmailSerializer(serializers.ModelSerializer):
    new_email = EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['new_email']

    def validate(self, attrs):
        new_email = User.objects.normalize_email(
            email=attrs.get('new_email').lower())
        old_email = User.objects.normalize_email(
            email=self.context['request'].user.email)

        if new_email == old_email:
            raise ValidationError(
                {'new_email': 'New mail should not be the same as old'})

        try:
            User.objects.get_by_email(new_email)
            raise MailAlreadyExists()
        except User.DoesNotExist:
            pass

        return super().validate(attrs)

    def send_confirm_new_email(self):
        UserService().send_new_email_activation_code(user=self.context['request'].user,
                                                     new_email=self.validated_data.get('new_email'))


class ConfirmNewEmailSerializer(serializers.Serializer):
    user = None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        code = attrs.get('code')
        cache = NewMailCache()
        new_email = cache.get_new_email(activation_email_code=code)

        if new_email is None:
            raise ValidationError({'code': f'Code expired {code}'})

        try:
            self.user = User.objects.all().get_by_activation_email(code)
        except User.DoesNotExist:
            raise ValidationError({'code': 'Not found'})

        return {'new_email': new_email, 'code': code}

    def confirm_new_email(self):
        UserService.confirm_new_email(
            user=self.user, new_email=self.validated_data.get('new_email'))


class CheckResetCodeSerializer(serializers.Serializer):
    code = CodeField()

    class Meta:
        fields = ['code']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            User.objects.get(
                reset_password_code=attrs.get('code'),
                reset_password_code_expire__gte=timezone.now()
            )
        except User.DoesNotExist:
            raise ResetCodeOrEmailInvalid()
        return {}


class ResetPasswordSerializer(CheckResetCodeSerializer):
    password = PasswordField()
    user: User

    class Meta:
        fields = ['email', 'code', 'password']

    def validate(self, attrs):
        super().validate(attrs)
        try:
            self.user = User.objects.all(
            ).get_by_reset_password_code(attrs['code'])
        except User.DoesNotExist:
            raise ResetCodeOrEmailInvalid()
        return attrs

    def reset_password(self):
        UserService.set_password(
            user=self.user, raw_new_password=self.validated_data.get('password'))


class ResendConfirmEmailSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def send_confirm_email(self):
        user = self.context['request'].user
        if user.email is None or user.email == "":
            raise ValidationError({'email': 'Mail not specified'})
        UserService().send_email_activation_code(user)

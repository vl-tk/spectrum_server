from datetime import timedelta

from apps.users.enums import UserStatuses, UserTypes
from apps.users.services.user import UserService
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import password_validation
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import (check_password, is_password_usable,
                                         make_password)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator, MinLengthValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from main.validators import (validate_avatar_max_size,
                             validate_document_file_max_size,
                             validate_images_file_max_size,
                             validate_phone_simple,
                             validate_supplier_document_ext)
from utils.file_storage import avatar_property_avatar_path


class UserQuerySet(models.QuerySet):
    def get_by_email(self, raw_login: str) -> 'User':
        return self.get(email=raw_login)

    def get_by_activation_code(self, code: str) -> 'User':
        return self.get(activation_email_code=code)

    def get_by_reset_password_code(self, code: str) -> 'User':
        return self.get(reset_password_code=code)

    def get_with_email_confirmed(self):
        return self.filter(is_email_active=True)

    def get_active(self):
        return self.filter(is_active=True)

    def get_not_banned(self):
        return self.filter(status=UserStatuses.ACTIVE.value)


class UserManager(BaseUserManager):

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def normalize_email(self, email_address):
        """
        Normalize the email address by lowercasing the domain part of it.
        """

        email_address = email_address or ''
        try:
            email_name, domain_part = email_address.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email_address = email_name.lower() + '@' + domain_part.lower()
        return email_address

    def _create_user(self, email: str, password: str, **extra_fields) -> 'User':
        with transaction.atomic():
            if not email:
                raise ValueError('Users must have an email address')
            if not password:
                raise ValueError('Users must have a password')
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)

            # TODO:
            if 'username' in extra_fields.keys():
                extra_fields.pop('username')

            user = self.model(email=self.normalize_email(email), **extra_fields)
            user.set_password(password)
            if settings.SEND_ACTIVATION_EMAIL is False or extra_fields.get('is_email_active'):
                user.is_email_active = True
            else:
                UserService().send_email_activation_code(user)
            user.save()
        return user

    def create_user(
                    self,
                    email: str,
                    password: str,
                    first_name: str = '',
                    last_name: str = '',
                    is_email_active: bool = False
                    ) -> 'User':
        user = self._create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_email_active=is_email_active
        )
        user.save()
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm') and callable(backend.with_perm):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractUser):

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    STATUSES = [
        (UserStatuses.ACTIVE.value, 'Active'),
        (UserStatuses.HARD_BANNED.value, 'Baned')
    ]

    email = models.CharField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator(), EmailValidator()],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    # common user info
    first_name = models.CharField(
        verbose_name=_('First name'),
        max_length=30,
        null=True,
        blank=True,
        validators=[MinLengthValidator(0)]
    )
    last_name = models.CharField(
        verbose_name=_('Last name'),
        max_length=30,
        null=True,
        blank=True,
        validators=[MinLengthValidator(0)]
    )
    avatar = models.ImageField(
        verbose_name=_("Avatar image"),
        upload_to=avatar_property_avatar_path,
        validators=[validate_avatar_max_size],
        null=True,
        blank=True
    )
    status = models.PositiveSmallIntegerField(
        _('Status'),
        choices=STATUSES,
        default=UserStatuses.ACTIVE.value
    )
    user_type = models.PositiveSmallIntegerField(
        _('User type'),
        choices=UserTypes.choices,
        default=UserTypes.CLIENT.value
    )

    # system info
    password = models.CharField(verbose_name=_('Password'), max_length=254, blank=False, null=False)
    is_active = models.BooleanField(
        _('Is active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_email_active = models.BooleanField(_('Email confirmed'), default=False)
    activation_email_code = models.CharField(
        max_length=32,
        verbose_name=_('Email confirmation code'),
        null=True, blank=True
    )
    email_activation_date = models.DateTimeField(blank=True, null=True)
    reset_password_code = models.CharField(
        max_length=32,
        verbose_name=_('Password reset code'),
        null=True, blank=True
    )
    reset_password_code_expire = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    objects = UserManager()

    # Stores the raw password if set_password() is called so that it can
    # be passed to password_changed() after the model is saved.
    _password = None

    def __str__(self):
        return f'#{self.pk} {self.email}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def set_password(self, raw_password: str):
        self._password = raw_password
        self.password = make_password(self._password, salt=settings.SECURE_AUTH_SALT)

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(password: str):
            self.set_password(password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    def hard_ban_user(self):
        self.status = UserStatuses.HARD_BANNED.value
        self.save()
        return self

    def unban_user(self):
        self.status = UserStatuses.ACTIVE.value

    def set_password_reset_code(self, code):
        self.reset_password_code = code
        self.reset_password_code_expire = timezone.now() + timedelta(days=1)

    def set_email_activation_code(self, code):
        self.activation_email_code = code

    def set_email(self, email):
        self.email = email

    def confirm_email(self):
        self.is_email_active = True
        self.activation_email_code = None
        self.email_activation_date=timezone.now()

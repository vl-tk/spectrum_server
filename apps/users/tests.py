import json
import shutil
from http.cookies import SimpleCookie
from pathlib import Path

from apps.users.enums import UserStatuses
from apps.users.errors import EmailNotActivated, UserIsHardBanned
from apps.users.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.exceptions import InvalidToken
from utils.email import SEND_CONFIRM_EMAIL_SUBJECT
from utils.test import (AuthClientTestCase, BaseUserTestCase,
                        get_alt_test_files, get_test_avatar_file,
                        get_test_files)


class TokenTestCase(AuthClientTestCase):
    credentials: dict

    def setUp(self) -> None:
        super().setUp()
        self.user = self.create_random_user(extra_fields={'is_email_active': True})

        self.credentials = {
            'email': self.user.email,
            'password': self.USER_PASSWORD,
        }
        self.client = self.create_client_with_auth(self.user)
        mail.outbox = []

    def test_get_token(self):
        response = self.client.post(reverse('token_obtain_pair'), self.credentials)
        tokens = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(tokens['access'])
        self.assertTrue(tokens['refresh'])
        response = self.client.post(reverse('token_verify'), {'token': tokens['access']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer %s' % tokens['access'])
        auth_client = self.client_class()
        auth_client.credentials(HTTP_AUTHORIZATION='Bearer %s' % tokens['access'])
        response = auth_client.post(reverse('token_check_auth'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_token_verify(self):
        access = 'eyJ0eXAiOiJKV1p2LCJhbGciOiJIUzI1NiJ9.' \
                 'eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwI' \
                 'joxNTg0Nzg1NDkxLCJqdGkiOiI3NDkyNzdlOG' \
                 'E0MzU0NDk5OTY2ZjFjZWI2ZDhlNGRmNSIsInV' \
                 'zZXJfaWQiOjV9.EDuzYiPjtyn9WrMcrueZC9IV0BTmWciq9U2TBFMIpw0'
        response = self.client.post(reverse('token_verify'), {'token': access})
        self.assertEqual(response.status_code, InvalidToken.status_code)
        self.assertEqual(response.data['detail'], InvalidToken.default_detail)
        self.assertEqual(response.data['code'], InvalidToken.default_code)

    def test_fail_email_get_token(self):
        data = self.credentials
        data['email'] = 'te3st23@exam22ple.ru'
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_password_get_token(self):
        data = self.credentials
        data['password'] = 'te3stasdasd'
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_password_and_email_get_token(self):
        data = self.credentials
        data['email'] = 'te3s45t23@exam2d2ple.ru'
        data['password'] = 'te3stas4332dasd'
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_token_for_admin_access_user(self):
        anonymous_client = self.client_class()
        credentials = {
            'email': self.staff_user.email,
            'password': self.USER_PASSWORD,
        }
        response = anonymous_client.post(
            reverse('token_obtain_pair'), credentials)
        tokens = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(tokens['access'])
        self.assertTrue(tokens['refresh'])
        response = anonymous_client.post(reverse('token_verify'), {
                                    'token': tokens['access']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        anonymous_client.credentials(
            HTTP_AUTHORIZATION='Bearer %s' % tokens['access'])
        response = anonymous_client.post(
            reverse('token_check_auth'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestClassAuthClientTestCase(BaseUserTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user = self.create_random_user(extra_fields={'is_email_active': True})
        self.client = self.create_client_with_auth(self.user)
        mail.outbox = []

    def test_is_authenticated_client(self):
        response = self.client.post(reverse('token_check_auth'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.hard_ban_user()
        self.user.save()
        response = self.client.post(reverse('token_check_auth'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'User is hard banned')
        self.assertEqual(response.data['code'], 'user_hard_banned')


class TestChangePassword(BaseUserTestCase):
    data = {
        'new_password': 'new_password',
    }

    def setUp(self):
        super().setUp()
        self.user = self.create_random_user(extra_fields={'is_email_active': True})
        self.client = self.create_client_with_auth(self.user)
        mail.outbox = []
        self.data['password'] = self.USER_PASSWORD

    def _get_change_password_response(self):
        return self.client.post(reverse('users:change_password'), data=self.data)

    def test_change_password(self):
        response = self._get_change_password_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data)

    def test_change_password_with_invalid_password(self):
        self.data['password'] = 'invalid_password'
        response = self._get_change_password_response()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'Wrong password')


class UserRegistrationsTestCase(AuthClientTestCase):

    def test_registration_without_name_successful(self):
        credentials = {
            'email': 'test@test.ru',
            'password': self.USER_PASSWORD
        }
        mail.outbox = []
        response = self.client.post(reverse('users:register'), data=credentials)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_without_password(self):

        credentials = {
            'email': 'test@test.ru',
            'first_name': 'Velvet',
            'last_name': 'Blasius',
        }
        mail.outbox = []
        response = self.client.post(reverse('users:register'), data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['password'][0]), 'Password is required')

        # empty password

        credentials = {
            'email': 'test@test.ru',
            'first_name': 'Velvet',
            'last_name': 'Blasius',
            'password': ''
        }
        mail.outbox = []
        response = self.client.post(reverse('users:register'), data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['password'][0]), 'Password is required')

    def test_registration_successful(self):

        self.assertEqual(User.objects.count(), 3)

        credentials = {
            'email': 'test@test.ru',
            'first_name': 'Velvet',
            'last_name': 'Blasius',
            'password': 'nbwLKygotXVPMcXJ'
        }
        mail.outbox = []
        response = self.client.post(reverse('users:register'), data=credentials)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 4)


class TestHardBanUser(AuthClientTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user = self.create_random_user()
        self.client = self.create_client_with_auth(self.user)
        mail.outbox = []

    def test_auth_after_hard_ban(self):

        self.second_user = self.create_random_user()
        self.second_client = self.create_client_with_auth(self.user)
        self.second_user.status = UserStatuses.HARD_BANNED.value
        self.second_user.save()

        credentials = {
            'email': self.second_user.email,
            'password': self.USER_PASSWORD
        }
        response = self.anonymous_client.post(reverse('token_obtain_pair'), credentials)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], UserIsHardBanned.default_detail)
        self.assertEqual(response.data['code'], UserIsHardBanned.default_code)


class NewConfirmEmailTestCase(AuthClientTestCase):
    def test_send_confirm_email(self):
        mail.outbox = []
        response = self.client.post(reverse("users:send_confirm_email"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(mail.outbox), 0)
        self.assertEqual(self.user.email, mail.outbox[0].to[0])
        self.assertIsNotNone(mail.outbox[0].body)


# class ResetPasswordTestCase(AuthClientTestCase):
#     def test_request_reset_password(self):
#         user = self.create_random_user(extra_fields={'is_email_active': True})
#         password_hash1 = user.password
#         self.assertIsNone(user.reset_password_code)
#         response = self.client.post(reverse("users:request_reset_password"), data={'email': user.email})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         user = User.objects.get(pk=user.pk)
#         self.assertNotEqual(password_hash1, user.password)

#     def test_send_request_reset_password_email(self):
#         mail.outbox.clear()
#         response = self.client.post(reverse("users:request_reset_password"), data={'email': self.user.email})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertGreater(len(mail.outbox), 0)
#         self.assertEqual(self.user.email, mail.outbox[0].to[0])
#         self.assertIsNotNone(mail.outbox[0].body)


class UserTestCase(AuthClientTestCase):

    def setUp(self):
        super().setUp()
        self.user.first_name = 'John'
        self.user.last_name = 'Johnson'
        self.user.email = 'test@example.com'
        self.user.save()

    def test_user_retrieve(self):
        response = self.client.get(reverse("users:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], self.user.pk)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Johnson')

    def test_user_partial_update_avatar(self):
        self.assertEqual(str(self.user.avatar), '')
        data = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': self.user.email,
        }
        payload = {
            'data': json.dumps(data),
            'avatar': get_test_avatar_file('avatar_img.png'),
        }
        response = self.client.patch(reverse("users:me"), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], self.user.pk)

        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(str(user.avatar).endswith('.png'))

    # def test_supplier_document_upload(self):

    #     # is not used if googlecloud is enabled
    #     if settings.DEFAULT_FILE_STORAGE.endswith('FileSystemStorage'):

    #         response = self.supplier_client.post(
    #             reverse('users:upload_supplier_document'),
    #             data={'file': self.test_data_service.get_random_file()},
    #             format='multipart'
    #         )
    #         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(Path(settings.MEDIA_ROOT) / 'avatars')
        except OSError as e:
            print(e)
        return super().tearDownClass()

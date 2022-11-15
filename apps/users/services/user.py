import secrets
import string

from apps.users.redis import NewMailCache
from apps.users.signals import (S_email_activation_code_created,
                                S_new_email_activation_code_created,
                                S_new_user_email_activated,
                                S_password_reset_code_created)
from django.contrib.auth import get_user_model
from utils.random import generate_unique_code


class UserService:

    @staticmethod
    def make_random_password(length=10):
        symbols = ['!', '#', '$', '-']
        password = ""
        for _ in range(length):
            password += secrets.choice(string.ascii_lowercase)
        password += secrets.choice(string.ascii_uppercase)
        password += secrets.choice(string.digits)
        password += secrets.choice(symbols)
        return password

    @staticmethod
    def make_random_username(*args, **kwargs):
        return 'test'

    # def send_make_new_password(self, user: 'User'):
    #     """ Generate new password and send it to email """
    #     new_password = UserService().make_random_password()
    #     user.set_password(new_password)
    #     user.save()
    #     S_new_password_created.send(
    #         sender=self.__class__,
    #         instance=user,
    #         new_password=new_password
    #     )

    def send_reset_password_code(self, user: 'User'):
        """ Generate password reset code and send it to email """

        code = generate_unique_code(cls_model=get_user_model(), field='reset_password_code', length=32)
        user.set_password_reset_code(code)
        user.save()
        S_password_reset_code_created.send(sender=self.__class__, instance=user)

    def send_reset_password_code(self, user: 'User'):
        """ Generate password reset code and send it to email """

        code = generate_unique_code(
            cls_model=get_user_model(), field='reset_password_code', length=32)
        user.set_password_reset_code(code)
        user.save()
        S_password_reset_code_created.send(
            sender=self.__class__, instance=user)

    def send_email_activation_code(self, user: 'User'):
        """ Generate email activation code and send it to user email """

        code = generate_unique_code(cls_model=get_user_model(), field='activation_email_code', length=32)
        user.set_email_activation_code(code)
        user.save()
        S_email_activation_code_created.send(sender=self.__class__, instance=user)

    def send_new_email_activation_code(self, new_email, user: 'User'):
        """ Generate new email activation code and send it to new email """

        code = generate_unique_code(cls_model=get_user_model(), field='activation_email_code', length=32)
        user.set_email_activation_code(code)
        user.save()
        NewMailCache().set_new_email(activation_email_code=user.activation_email_code, new_email=new_email)
        S_new_email_activation_code_created.send(sender=self.__class__, instance=user, new_email=new_email)

    @classmethod
    def confirm_email(cls, user: 'User'):
        user.confirm_email()
        S_new_user_email_activated.send(sender=cls, instance=user)
        user.save()

    @classmethod
    def confirm_new_email(cls, user: 'User', new_email: str):
        user.set_email(new_email)
        user.confirm_email()
        S_new_user_email_activated.send(sender=cls, instance=user)
        user.save()

    @staticmethod
    def set_password(user: 'User', raw_new_password: str):
        user.set_password(raw_new_password)
        user.save()

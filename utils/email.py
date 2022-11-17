from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template
from django.template.loader import get_template

SEND_CONFIRM_EMAIL_SUBJECT = 'Email confirmation'
SEND_RESET_PASSWORD_SUBJECT = 'Password recovery of your account'
SEND_FAVORITES_LINK_EMAIL = 'Избранные проекты'
SUBJECT_NEED_TO_CALL = 'Заказан звонок'
SUBJECT_NEW_REQUEST = 'Новая заявка на проект'
SUBJECT_CONFIRMATION = 'Благодарим за заявку'


def __main_client_terms_endpoint():
    return '%s%s' % (settings.BASE_CLIENT_URL, '/terms-of-service')


def __send_mail(plaintext: Template, html: Template, to_emails, context=None,
                subject='Info', from_email=settings.EMAIL_FROM):
    if context is None:
        context = {}

    context['BASE_CLIENT_URL'] = settings.BASE_CLIENT_URL
    context['logo_url'] = f'{settings.BASE_CLIENT_URL}/images/logo.png'
    text_content = plaintext.render(context)
    html_content = html.render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 from_email=from_email, to=to_emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_favorite_link_email(emails: list, link: str):
    __send_mail(
        plaintext=get_template('emails/favorites/content.txt'),
        html=get_template('emails/favorites/content.html'),
        context={
            'url': link
        },
        subject=SEND_FAVORITES_LINK_EMAIL,
        to_emails=emails
    )


def send_contacts_call_mail(emails: list, data: dict) -> None:
    __send_mail(
        plaintext=get_template('emails/new_call/content.txt'),
        html=get_template('emails/new_call/content.html'),
        context=data.copy(),
        subject=SUBJECT_NEED_TO_CALL,
        to_emails=emails
    )


def send_contacts_request_mail(emails: list, data: dict) -> None:
    __send_mail(
        plaintext=get_template('emails/new_request/content.txt'),
        html=get_template('emails/new_request/content.html'),
        context=data.copy(),
        subject=SUBJECT_NEW_REQUEST,
        to_emails=emails
    )


def send_confirm_email(emails: list, code: str, user: 'User'):
    __send_mail(
        plaintext=get_template('emails/users/confirm/content.txt'),
        html=get_template('emails/users/confirm/content.html'),
        context={
            'url': '%s%s' % (settings.BASE_CLIENT_URL, '/confirm/email/%s' % code),
            'user': user,
            'email_from': settings.EMAIL_FROM
        },
        subject=SEND_CONFIRM_EMAIL_SUBJECT,
        to_emails=emails
    )

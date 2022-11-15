from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.translation import gettext as _
from mutagen import File
from rest_framework.exceptions import ValidationError

validate_phone = RegexValidator(
    regex=r'^((\+1|\+7|)\d{3}\d{3}\d{4})$',
    message="Enter the correct phone number"
)

validate_phone_simple = RegexValidator(
    regex=r'^\d{2,16}$',
    message="Enter the correct phone number (2-16 digits)"
)

validate_phone_simple_amsterdam = RegexValidator(
    regex=r'^\d{9}$',
    message="Enter the correct phone number"
)

validate_zipcode_simple = RegexValidator(
    regex=r'^\d{4}[a-zA-Z]{2}|\d{4}\s[a-zA-Z]{2}$',
    message="Enter zip code in the format: 0000AZ"
)

validate_supplier_document_ext = FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])

validate_ep_document = FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xlsx', 'xls'])

validate_ep_schema = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])

validate_deal_file = FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'])

validate_video_ext = FileExtensionValidator(allowed_extensions=['mp4'])

validate_audio_ext = FileExtensionValidator(allowed_extensions=['mp3', 'm4u'])


def validate_max_count_files(value, max_count):
    if len(value) > max_count:
        raise ValidationError(
            f"The number of files cannot exceed {max_count}")
    return value


def validate_avatar_max_size(value):
    file_size = value.size
    file_size_limit_mb = 10
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


def validate_images_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 10
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


def validate_video_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 200
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


def validate_audio_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 200
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


def validate_preview_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 10
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


def validate_document_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 25
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)


validate_youtube = RegexValidator(
    regex=r'youtube.com|youtu.be',
    message='Only YouTube videos allowed'
)

validate_only_numbers = RegexValidator(regex=r'^\d+$', message='The field must contain only numbers')


def validate_decimals(value):
    if len(str(value).split('.')[-1]) > 3:
        raise ValidationError({'quantity': "The value should have maximum 3 numbers after the dot"})
    return value

def validate_imperial_value_decimals(value):
    if len(str(value).split('.')[-1]) > 6:
        raise ValidationError({'quantity': "The value should have maximum 6 numbers after the dot"})
    return value


class CustomPasswordValidator:

    SPECIAL_CHARS = "~!@#$%^&*_-+=`|(){}[]:;\"'<>,.?/"

    def validate(self, password, user=None):

        import string

        svalid = False
        for c in list(self.SPECIAL_CHARS):
            if c in password:
                svalid = True
                break

        if not svalid:
            raise ValidationError(
                _(f"This password must contain at least one of the characters: {self.SPECIAL_CHARS}"),
                code='password_no_special_chars'
            )

        string.digits

        uvalid = False
        for c in list(string.ascii_uppercase):
            if c in password:
                uvalid = True
                break

        if not uvalid:
            raise ValidationError(
                _(f"This password must contain at least one uppercase letter"),
                code='password_no_uppercase_letters'
            )

        dvalid = False
        for c in list(string.digits):
            if c in password:
                dvalid = True
                break

        if not dvalid:
            raise ValidationError(
                _(f"This password must contain at least one digit"),
                code='password_no_digits'
            )

    def get_help_text(self):
        return _(
            f"Your password must contain any of the special characters: {self.SPECIAL_CHARS}"
        )

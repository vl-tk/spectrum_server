from rest_framework.exceptions import ValidationError


def validate_support_file_max_size(value):
    file_size = value.size
    file_size_limit_mb = 10
    limit_kb = file_size_limit_mb * 1024 * 1024
    if file_size > limit_kb:
        raise ValidationError("Maximum file size %s MB" % file_size_limit_mb)

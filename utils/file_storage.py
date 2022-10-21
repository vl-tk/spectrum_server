import mimetypes
import os
from hashlib import md5


def get_filename_by_hash(file, filename) -> str:
    file.seek(0)
    file_hash = md5(file.read()).hexdigest()
    return f"{file_hash}.{filename.split('.')[-1]}"


def get_file(instance, prop_name=None):
    if prop_name is not None:
        return getattr(instance, prop_name).file
    return instance.file.file


def delete_image(image):
    return image.delete(True)


def get_storage_path_unique(instance, filename, directory):
    filename_hash = get_filename_by_hash(get_file(instance, 'sample'), filename)
    return f"{directory}/{filename_hash[0:10]}/{filename_hash[10:]}"


def get_storage_path_static(key, filename, directory):
    return f"{directory}/{key}/{filename}"


def avatar_property_avatar_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return get_storage_path_static(instance.pk, f"avatar{file_extension}", 'avatars')


def preview_property_preview_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return get_storage_path_static(instance.pk, f"preview{file_extension}", 'previews')


def get_file_mime(filename):
    return mimetypes.guess_type(filename)

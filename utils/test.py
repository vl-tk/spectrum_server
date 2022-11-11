from pathlib import Path

from django.conf import settings
from django.core.files import File


def get_test_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image1.jpg', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image2.jpg', mode='rb')),
    ]


def get_test_document_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-example_PDF_1MB.pdf', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-sample_1MB.docx', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-sample_1MB.doc', mode='rb')),
    ]


def get_test_excel_file() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / '2gis_test_mini.xlsx', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / '2gis_test_big.xlsx', mode='rb'))
    ]

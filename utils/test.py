import json
import random
from itertools import groupby
from pathlib import Path

from apps.users.enums import UserTypes
from apps.users.models import User
from apps.users.tokens.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.core.files import File
from mimesis import Datetime, Person, Text
from mimesis.builtins import RussiaSpecProvider
from mimesis.enums import Gender
from mimesis.locales import Locale
from mimesis.random import get_random_item
from rest_framework.test import APIClient, APITestCase
from utils.random import random_simple_string
from utils.vcr import VCRMixin


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
        File(open(Path(settings.TEST_FILES_ROOT) / 'events_test_mini.xlsx', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'events_test_mini_2.xlsx', mode='rb')),
        # File(open(Path(settings.TEST_FILES_ROOT) / '2gis_test_big.xlsx', mode='rb'))
    ]



class UserFactoryMixin:
    USER_PASSWORD = 'sdw332!4TdSD'

    @staticmethod
    def __random_char(length=10, repeat=1):
        return ''.join(random_simple_string(length) for _ in range(repeat))

    @staticmethod
    def make_random_username(*args, **kwargs):
        return 'test'

    @staticmethod
    def make_random_password():
        return self.USER_PASSWORD

    def create_user(self,
                    username: str,
                    password: str,
                    first_name: str,
                    last_name: str,
                    extra_fields: dict
                    ) -> 'User':

        if len(first_name) == 0:
            first_name = 'None'
        if len(last_name) == 0:
            last_name = 'None'

        user = User.objects._create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.save()
        return user

    def create_random_user(self,
                            username='',
                            password='',
                            gender=None,
                            user_type=None,
                            extra_fields={}
                            ) -> 'User':

        from apps.users.services.user import UserService

        person = Person(Locale.RU)
        r = RussiaSpecProvider()

        gender = gender if gender else get_random_item(Gender)

        if user_type is None:
            user_type = random.choice([UserTypes.CLIENT.value, UserTypes.PUBLISHER.value])

        data = {
            'is_active': True,
            'is_email_active': True,
            'email': person.email(),
            'user_type': user_type,
            # 'phone_number': person.telephone(mask='+7-###-###-####'),
            # 'passport_series': r.passport_series(),
            # 'passport_number': r.passport_number(),
            # 'passport_date': Datetime(Locale.RU).formatted_date('%d.%m.%Y'),
            # 'inn': r.inn(),
            # 'snils': r.snils()
        }

        # if user_type == UserTypes.STUDENT.value:

        #     data['avg_score'] = random.randint(30, 50) / 10

        # else:

        #     data['work_field'] = random.choice([
        #         'Фундаментальная медицина',
        #         'Биотехнологии',
        #         'Юриспруденция',
        #         'Компьютерные технологии'
        #     ])

        #     data['work_experience'] = random.randint(1, 25)
        #     data['scientific_rank'] = random.choice(['Кандидат наук', 'Доктор наук'])
        #     data['teacher_rank'] = random.randint(30, 50) / 10

        data.update(extra_fields)

        first_name = person.first_name(gender=gender)
        # middle_name = r.patronymic(gender=gender)
        last_name = person.last_name(gender=gender)

        user = self.create_user(
            username=username or UserService.make_random_username(first_name, last_name),
            password=password or self.USER_PASSWORD,
            first_name=first_name,
            last_name=last_name,
            extra_fields=data
        )

        # if user_type == UserTypes.STUDENT.value:
        #     if gender == Gender.FEMALE.value:
        #         user.photo = get_test_photo_files()[1]
        #     else:
        #         user.photo = get_test_photo_files()[0]
        # else:
        #     if gender == Gender.FEMALE.value:
        #         user.photo = get_test_photo_files()[3]
        #     else:
        #         user.photo = get_test_photo_files()[2]

        return user

    @staticmethod
    def create_client_with_auth(user: 'User') -> APIClient:
        token = TokenObtainPairSerializer.get_token(user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer %s' % token.access_token)
        return client


def get_test_photo_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'student_m.png', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'student_f.png', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'teacher_m.png', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'teacher_f.png', mode='rb')),
    ]

def get_test_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image1.jpg', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image2.jpg', mode='rb')),
    ]


def get_alt_test_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image3.jpg', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'test_image4.jpg', mode='rb')),
    ]


def get_test_avatar_file(filename) -> File:
    # TODO
    return File(open(Path(settings.TEST_FILES_ROOT) / 'teacher_m.png', mode='rb'))


def get_test_video_file() -> File:
    return File(open(Path(settings.TEST_FILES_ROOT) / 'file.mp4', mode='rb'))


def get_test_document_files() -> list:
    return [
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-example_PDF_1MB.pdf', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-sample_1MB.docx', mode='rb')),
        File(open(Path(settings.TEST_FILES_ROOT) / 'file-sample_1MB.doc', mode='rb')),
    ]


class TestDataService(UserFactoryMixin):

    DEFAULT_ENTITIES_COUNT = 10

    def get_random_file(self):
        return random.choice(get_test_document_files())

    def create_random_item(self,
                        publisher,
                        title: str = None,
                        status: int = None,
        ):
        """Generate random item with sensible defaults"""

        if title is None:
            text = Text('ru')
            title = text.text(quantity=1)

        # is_active = True if is_active is None else is_active

        # max_application_count = None if max_application_count is None else max_application_count

        # if start_date is None:
        #     start_date = timezone.now() - timedelta(days=random.randint(1, 10))

        # if end_date is None:
        #     end_date = timezone.now() + timedelta(days=random.randint(1, 10))

        i = Item(
            title=title,
            publisher=publisher,
            publish_status=PublishStatus.APPROVED.value
        )
        i.save()
        return i

class BaseUserTestCase(VCRMixin, APITestCase, UserFactoryMixin):
    pass


class AuthClientTestCase(BaseUserTestCase):

    staff_user: User
    staff_client: APIClient
    anonymous_client: APIClient

    test_data_service = TestDataService()

    def setUp(self):
        super().setUp()

        self.user = self.create_random_user(
            password=self.USER_PASSWORD,
            user_type=UserTypes.CLIENT.value,
            extra_fields={'is_email_active': True}
        )
        self.client = self.create_client_with_auth(self.user)

        self.publisher_user = self.create_random_user(
            password=self.USER_PASSWORD,
            user_type=UserTypes.PUBLISHER.value,
            extra_fields={'is_email_active': True}
        )
        self.publisher_client = self.create_client_with_auth(self.publisher_user)

        self.staff_user = self.create_random_user(
            password=self.USER_PASSWORD,
            extra_fields={'is_staff': True, 'is_email_active': True}
        )
        self.staff_client = self.create_client_with_auth(user=self.staff_user)

        self.anonymous_client = self.client_class()


def get_nth_group_of_values(iterable, key, n=1):
    """
    if we need 1st, 2nd or any other group of values from some items

    usually to check sorted items' values

    https://stackoverflow.com/questions/44641031/splitting-list-into-smaller-lists-of-equal-values

    supports objects and dicts

    see test_get_nth_group_of_values for examples
    """

    if hasattr(iterable[0], 'keys'):
        dicts = iterable
    else:
        dicts = [i.__dict__ for i in iterable]  # make dicts if objects

    assert any([bool(key in i) for i in dicts])

    values = [i.get(key) for i in dicts]

    found_values = [list(grp) for k, grp in groupby(values)][n - 1]

    return found_values


def _get_json(path):
    return json.loads(Path(settings.PROJECT_DIR).joinpath(path).read_text())

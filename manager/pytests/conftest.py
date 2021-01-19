import pytest
from django.utils import timezone
from rest_framework_api_key.models import APIKey

from manager.models import Target, Source, StaticTarget
from manager.tasks import parse_sources


@pytest.fixture
def create_source(db):

    def make_create_source(name='Test', url='test.com/', limit=1, is_active=True):
        return Source.objects.create(name=name, url=url, limit=limit, is_active=is_active)

    return make_create_source


@pytest.fixture
def create_target(db):

    def make_create_target(source, url='test1.com', traffic=0, publish_time=timezone.now()):
        return Target.objects.create(source=source, url=url, traffic=traffic, publish_time=publish_time)

    return make_create_target


@pytest.fixture
def create_static_target(db):

    def make_create_static_target(name='Test', url='static-test.com/', is_active=True):
        return StaticTarget.objects.create(name=name, url=url, is_active=is_active)

    return make_create_static_target


@pytest.fixture
def call_parse_sources(db):

    def make_call_parse_sources():
        parse_sources()

    return make_call_parse_sources


@pytest.fixture(scope='module')
def auth_header(django_db_blocker):

    with django_db_blocker.unblock():
        api_key_obj, key = APIKey.objects.create_key(name='Test')

    return {'HTTP_AUTHORIZATION': f'Api-Key {key}'}

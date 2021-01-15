import logging

import pytest

from manager.models import Target


# Some successful tests may log error messages, disabled them to avoid confusion
logging.disable()


@pytest.mark.django_db
def test_only_last_five_targets_added(create_source, call_parse_sources):
    create_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')

    call_parse_sources()

    assert Target.objects.count() == 5


@pytest.mark.django_db
def test_incomplete_feed_is_parsed_properly(create_source, call_parse_sources):
    create_source(url='http://127.0.0.1:8000/static/tests/mock_feed_incomplete.xml')

    call_parse_sources()

    assert Target.objects.count() == 4


@pytest.mark.django_db
def test_targets_not_duplicated(create_source, call_parse_sources):
    source = create_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')

    call_parse_sources()

    # simulate updated feed
    source.url = 'http://127.0.0.1:8000/static/tests/mock_feed_updated.xml'
    source.save()

    call_parse_sources()

    assert Target.objects.count() == 6


@pytest.mark.django_db
def test_not_active_source_is_not_parsed(create_source, call_parse_sources):
    create_source(is_active=False)

    call_parse_sources()

    assert Target.objects.count() == 0


@pytest.mark.django_db
def test_parser_continue_work_if_source_is_not_responding(create_source, call_parse_sources):
    create_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')
    create_source(url='http://127.0.0.2:8000/static/tests/mock_feed.xml')

    call_parse_sources()

    assert Target.objects.count() == 5


@pytest.mark.django_db
def test_parser_continue_work_if_feed_is_not_found(create_source, call_parse_sources):
    create_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')
    create_source(url='http://127.0.0.1:8000/static/tests/mock_feed_not_exist.xml')

    call_parse_sources()

    assert Target.objects.count() == 5

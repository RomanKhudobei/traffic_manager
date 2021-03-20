import datetime as dt

import pytz
from django.urls import reverse

import pytest
from freezegun import freeze_time


@pytest.mark.django_db
def test_target_returned_in_response(create_source, create_target, client, auth_header):
    target = create_target(create_source())

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert random_targets == [target.url]


@pytest.mark.django_db
def test_one_random_target_returned_from_each_source(create_source, create_target, client, auth_header):
    source1 = create_source(url='source1.com', limit=5)
    target11 = create_target(source1, url='source1.com/page-1')
    target12 = create_target(source1, url='source1.com/page-2')

    source2 = create_source(url='source2.com', limit=5)
    target21 = create_target(source2, url='source2.com/page-1')
    target22 = create_target(source2, url='source2.com/page-2')

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert all([
        (target11.url in random_targets) or (target12.url in random_targets),
        (target21.url in random_targets) or (target22.url in random_targets),
    ])


@pytest.mark.django_db
def test_target_traffic_increases(create_source, create_target, client, auth_header):
    target = create_target(create_source())

    client.get(reverse('manager:random_targets'), **auth_header)

    target.refresh_from_db()
    assert target.traffic == 1


@pytest.mark.django_db
def test_source_remaining_traffic_decreases(create_source, create_target, client, auth_header):
    source = create_source()
    create_target(source)

    client.get(reverse('manager:random_targets'), **auth_header)

    source.refresh_from_db()
    assert source.remaining_traffic == 0


@pytest.mark.django_db
def test_source_remaining_traffic_decreases_for_yesterday_targets(create_source, create_target, client, auth_header):
    today = dt.datetime.now(tz=pytz.timezone('Europe/Kiev')).replace(hour=1, minute=0, second=0, microsecond=0)
    yesterday = (today - dt.timedelta(days=1)).replace(hour=23)

    with freeze_time(yesterday) as frozen_time:
        source = create_source()
        create_target(source)

        frozen_time.move_to(today)

        client.get(reverse('manager:random_targets'), **auth_header)

        source.refresh_from_db()
        assert source.remaining_traffic == 0


@pytest.mark.django_db
def test_target_traffic_not_overcomes_source_limit(create_source, create_target, client, auth_header):
    create_target(create_source())

    client.get(reverse('manager:random_targets'), **auth_header)
    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert random_targets == []


@pytest.mark.django_db
def test_no_targets_are_returned_from_not_active_source(create_source, create_target, client, auth_header):
    create_target(create_source(is_active=False))

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert random_targets == []


@pytest.mark.slow
@pytest.mark.django_db
def test_one_of_last_five_published_targets_are_returned(create_source, create_target, client, auth_header):
    limit = 100
    source = create_source(url='test.com', limit=limit)

    for i in range(1, 7):
        publish_time = dt.datetime.now() - dt.timedelta(days=i)
        create_target(source, url=f'test.com/page-{i}', publish_time=publish_time)

    for _ in range(limit):
        response = client.get(reverse('manager:random_targets'), **auth_header)
        random_targets = response.data

        assert 'test.com/page-6' not in random_targets


@pytest.mark.django_db
def test_static_target_returned_in_response(create_static_target, client, auth_header):
    static_target = create_static_target()

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert random_targets == [static_target.url]


@pytest.mark.django_db
def test_static_target_traffic_increases(create_static_target, client, auth_header):
    static_target = create_static_target()

    client.get(reverse('manager:random_targets'), **auth_header)

    static_target.refresh_from_db()
    assert static_target.traffic == 1


@pytest.mark.django_db
def test_static_target_not_overcomes_limit(create_static_target, client, auth_header):
    static_target = create_static_target()

    client.get(reverse('manager:random_targets'), **auth_header)
    client.get(reverse('manager:random_targets'), **auth_header)

    static_target.refresh_from_db()
    assert static_target.traffic == 1


@pytest.mark.django_db
def test_not_active_static_targets_is_not_returned(create_static_target, client, auth_header):
    create_static_target(is_active=False)

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.json()

    assert random_targets == []


@pytest.mark.django_db
def test_static_targets_without_limit_always_returned_in_response(create_source, create_target, create_static_target, client, auth_header):
    source1 = create_source(url='source1.com', limit=5)
    create_target(source1, url='source1.com/page-1')
    create_target(source1, url='source1.com/page-2')

    source2 = create_source(url='source2.com', limit=5)
    create_target(source2, url='source2.com/page-1')
    create_target(source2, url='source2.com/page-2')

    static_target1 = create_static_target(url='static-target1.com', limit=-1)
    static_target2 = create_static_target(url='static-target2.com', limit=-1)

    for _ in range(10):
        response = client.get(reverse('manager:random_targets'), **auth_header)
        random_targets = response.data

        assert all([
            static_target1.url in random_targets,
            static_target2.url in random_targets,
        ])


@pytest.mark.django_db
def test_targets_not_returned_without_api_key(create_source, create_target, client):
    create_target(create_source())

    response = client.get(reverse('manager:random_targets'))

    assert response.status_code == 403


@pytest.mark.django_db
def test_only_today_published_targets_are_accounted_for_traffic_limit(create_source, create_target, client, auth_header):
    source = create_source(url='test.com/rss', limit=5)

    create_target(source, url='test.com/page-1', publish_time=dt.datetime.now() - dt.timedelta(days=1), traffic=5)
    create_target(source, url='test.com/page-2')

    response = client.get(reverse('manager:random_targets'), **auth_header)
    random_targets = response.data

    assert any([
        random_targets == ['test.com/page-1'],
        random_targets == ['test.com/page-2'],
    ])

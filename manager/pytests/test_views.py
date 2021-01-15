import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_target_returned_in_response(create_source, create_target, client):
    source = create_source()
    target = create_target(source)

    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert random_targets == [target.url]


@pytest.mark.django_db
def test_one_random_target_returned_from_each_source(create_source, create_target, client):
    source1 = create_source()
    target11 = create_target(source1, url='test11.com')
    target12 = create_target(source1, url='test12.com')

    source1 = create_source(name='Test2', url='test2.com')
    target21 = create_target(source1, url='test11.com')
    target22 = create_target(source1, url='test12.com')

    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert all([
        (target11.url in random_targets) or (target12.url in random_targets),
        (target21.url in random_targets) or (target22.url in random_targets),
    ])


@pytest.mark.django_db
def test_target_traffic_increases(create_source, create_target, client):
    source = create_source()
    target = create_target(source)

    client.get(reverse('manager:random_targets'))

    target.refresh_from_db()
    assert target.traffic == 1


@pytest.mark.django_db
def test_target_traffic_not_overcomes_source_limit(create_source, create_target, client):
    source = create_source()
    create_target(source)

    client.get(reverse('manager:random_targets'))
    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert random_targets == []


@pytest.mark.django_db
def test_no_targets_are_returned_from_not_active_source(create_source, create_target, client):
    source = create_source(is_active=False)
    create_target(source)

    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert random_targets == []


@pytest.mark.django_db
def test_one_of_last_five_published_targets_are_returned(create_source, create_target, client):
    limit = 1000
    source = create_source(limit=limit)

    for i in range(1, 7):
        create_target(source, url=f'test{i}.com')

    for _ in range(limit):
        response = client.get(reverse('manager:random_targets'))
        random_targets = response.data

        assert 'test6.com' not in random_targets


@pytest.mark.django_db
def test_static_target_returned_in_response(create_static_target, client):
    static_target = create_static_target()

    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert random_targets == [static_target.url]


@pytest.mark.django_db
def test_not_active_static_targets_is_not_returned(create_static_target, client):
    create_static_target(is_active=False)

    response = client.get(reverse('manager:random_targets'))
    random_targets = response.data

    assert random_targets == []


@pytest.mark.django_db
def test_static_targets_always_returned_in_response(create_source, create_target, create_static_target, client):
    source1 = create_source(limit=5)
    create_target(source1, url='test11.com')
    create_target(source1, url='test12.com')

    source2 = create_source(name='Test2', url='test2.com', limit=5)
    create_target(source2, url='test21.com')
    create_target(source2, url='test22.com')

    static_target1 = create_static_target()
    static_target2 = create_static_target(name='Test2', url='static-test2.com')

    for _ in range(10):
        response = client.get(reverse('manager:random_targets'))
        random_targets = response.data

        assert all([
            static_target1.url in random_targets,
            static_target2.url in random_targets,
        ])


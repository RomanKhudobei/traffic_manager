import pytest
import datetime as dt
from django.urls import reverse


@pytest.mark.django_db
def test_statistic_view_return_404_without_name_parameter(create_source, create_target, client):
    create_target(create_source())

    response = client.get(reverse('source_statistic'))

    assert response.status_code == 404


@pytest.mark.django_db
def test_statistic_view_return_404_with_name_not_exist(create_source, create_target, client):
    create_target(create_source())

    response = client.get(reverse('source_statistic'), {'name': 'not-exist'})

    assert response.status_code == 404


@pytest.mark.django_db
def test_statistic_view_not_fail_with_invalid_date_parameter(create_source, create_target, client):
    create_target(create_source(name='Test'))

    response = client.get(reverse('source_statistic'), {'name': 'Test', 'date': 'invalid-date'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_statistic_view_works_with_future_date_parameter(create_source, create_target, client):
    future_date = dt.date.today() + dt.timedelta(days=1)
    create_target(create_source(name='Test'))

    response = client.get(reverse('source_statistic'), {'name': 'Test', 'date': future_date.isoformat()})

    assert response.status_code == 200
    assert future_date.isoformat() not in response.content.decode()


@pytest.mark.django_db
def test_statistic_view_works_without_targets(create_source, client):
    create_source(name='Test')

    response = client.get(reverse('source_statistic'), {'name': 'Test'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_statistic_view(create_source, create_target, client):
    today = dt.date.today()
    source = create_source(name='Test')
    target = create_target(source)

    response = client.get(reverse('source_statistic'), {'name': 'Test', 'date': today.isoformat()})

    assert response.status_code == 200
    assert today.isoformat() in response.content.decode()
    assert target.url in response.content.decode()
    assert target.title in response.content.decode()
    assert source.name in response.content.decode()

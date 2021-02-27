import pytest
import datetime as dt
from django.urls import reverse


@pytest.mark.django_db
def test_statistic_view_return_404_with_invalid_token(create_source, create_target, client):
    create_target(create_source())

    response = client.get(reverse('source_statistic', kwargs={'token': 'invalid-token'}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_statistic_view_not_fail_with_invalid_date_parameter(create_source, create_target, client):
    source = create_source()
    create_target(source)

    response = client.get(
        reverse('source_statistic', kwargs={'token': source.statistic_view_token}),
        {'date': 'invalid-date'}
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_statistic_view_works_with_future_date_parameter(create_source, create_target, client):
    source = create_source()
    create_target(source)

    future_date = dt.date.today() + dt.timedelta(days=1)
    response = client.get(
        reverse('source_statistic', kwargs={'token': source.statistic_view_token}),
        {'date': future_date.isoformat()}
    )

    assert response.status_code == 200
    assert future_date.isoformat() not in response.content.decode()


@pytest.mark.django_db
def test_statistic_view_works_without_targets(create_source, client):
    source = create_source()

    response = client.get(reverse('source_statistic', kwargs={'token': source.statistic_view_token}))

    assert response.status_code == 200


@pytest.mark.django_db
def test_statistic_view(create_source, create_target, client):
    source = create_source(name='Test')
    target = create_target(source)

    today = dt.date.today()

    response = client.get(
        reverse('source_statistic', kwargs={'token': source.statistic_view_token}),
        {'date': today.isoformat()}
    )

    assert response.status_code == 200
    assert today.isoformat() in response.content.decode()
    assert target.url in response.content.decode()
    assert target.title in response.content.decode()
    assert source.name in response.content.decode()

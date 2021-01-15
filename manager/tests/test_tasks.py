import logging

from django.test import TestCase

from manager.models import Source, Target
from manager.tasks import parse_sources


# Some successful tests may log error messages, disabled them to avoid confusion
logging.disable()


class ParseSourcesTestCase(TestCase):

    def setUp(self):
        print('Make sure "python manage.py runserver" is running')

    def get_source(self, name='Test', url='test.com/', limit=1, is_active=True):
        return Source.objects.create(name=name, url=url, limit=limit, is_active=is_active)

    def call_parse_sources(self):
        parse_sources()

    def test_only_last_five_targets_added(self):
        self.get_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')

        self.call_parse_sources()

        self.assertEqual(5, Target.objects.count())

    def test_targets_not_duplicated(self):
        source = self.get_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')

        self.call_parse_sources()

        # simulate updated feed
        source.url = 'http://127.0.0.1:8000/static/tests/mock_feed_updated.xml'
        source.save()

        self.call_parse_sources()

        self.assertEqual(6, Target.objects.count())

    def test_not_active_source_is_not_parsed(self):
        self.get_source(is_active=False)

        self.call_parse_sources()

        self.assertEqual(0, Target.objects.count())

    def test_parser_continue_work_if_source_is_not_responding(self):
        self.get_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')
        self.get_source(url='http://127.0.0.2:8000/static/tests/mock_feed.xml')

        self.call_parse_sources()

        self.assertEqual(5, Target.objects.count())

    def test_parser_continue_work_if_feed_is_not_found(self):
        self.get_source(url='http://127.0.0.1:8000/static/tests/mock_feed.xml')
        self.get_source(url='http://127.0.0.1:8000/static/tests/mock_feed_not_exist.xml')

        self.call_parse_sources()

        self.assertEqual(5, Target.objects.count())

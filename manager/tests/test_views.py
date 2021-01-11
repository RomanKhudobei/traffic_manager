import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from manager.models import Source, Target


class RandomTargetsViewTestCases(TestCase):

    def get_source(self, name='Test', url='test.com/', limit=1, is_active=True):
        return Source.objects.create(name=name, url=url, limit=limit, is_active=is_active)

    def get_target(self, source, url='test1.com', traffic=0, publish_time=timezone.now()):
        return Target.objects.create(source=source, url=url, traffic=traffic, publish_time=publish_time)

    def test_target_returned_in_response(self):
        source = self.get_source()
        target = self.get_target(source)

        random_targets = self.client.get(reverse('manager:random_targets'))

        self.assertJSONEqual(random_targets.content.decode(), [target.url])

    def test_one_random_target_returned_from_each_source(self):
        source1 = self.get_source()
        target11 = self.get_target(source1)
        target12 = self.get_target(source1)

        source2 = self.get_source(name='Test2', url='test2.com/')
        target21 = self.get_target(source2)
        target22 = self.get_target(source2)

        random_targets = json.loads(
            self.client.get(reverse('manager:random_targets')).content.decode()
        )

        source1.refresh_from_db()
        source2.refresh_from_db()
        self.assertTrue(all([
            any([target11.url in random_targets, target12.url in random_targets]),
            any([target21.url in random_targets, target22.url in random_targets])
        ]))

    def test_target_traffic_increases(self):
        source = self.get_source()
        target = self.get_target(source)

        self.client.get(reverse('manager:random_targets'))

        target.refresh_from_db()
        self.assertEquals(target.traffic, 1)

    def test_target_traffic_not_overcomes_source_limit(self):
        source = self.get_source()
        target = self.get_target(source)

        self.client.get(reverse('manager:random_targets'))
        random_targets = self.client.get(reverse('manager:random_targets'))

        target.refresh_from_db()

        self.assertJSONEqual(random_targets.content.decode(), [])

    def test_no_targets_are_returned_from_not_active_source(self):
        source = self.get_source(is_active=False)
        target = self.get_target(source)

        random_targets = self.client.get(reverse('manager:random_targets'))

        target.refresh_from_db()

        self.assertEquals(target.traffic, 0)
        self.assertJSONEqual(random_targets.content.decode(), [])

    def test_one_of_last_five_published_targets_are_returned(self):
        source = self.get_source(limit=1000)

        for i in range(1, 7):
            self.get_target(source, url=f'test{i}.com/')

        for _ in range(1000):
            random_targets = json.loads(
                self.client.get(reverse('manager:random_targets')).content.decode()
            )
            self.assertNotIn('test6.com/', random_targets)

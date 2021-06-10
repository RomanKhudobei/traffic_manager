import logging
import datetime as dt
import time
import pytz

import feedparser
from django.core.exceptions import MultipleObjectsReturned

from manager.models import Target


logger = logging.getLogger(__name__)


class SourceParser:

    def __init__(self, source):
        """
        :param source: source object
        :type source: manager.models.Source
        """
        self.__source = source
        self.__items = []

    def parse(self):
        """
        Parses given source object and saves five last items from feed as Target elements to database

        :raises urllib.error.URLError: connection issues
        :raises ValueError: Feed not found, invalid or empty
        """
        feed = feedparser.parse(self.__source.url)

        self.__items = feed.get('entries', [])[:5]

        if len(self.__items) == 0:
            raise ValueError('Feed is not found, empty or improperly parsed')

    def save(self):

        for item in self.__items:
            publish_time = self.__extract_publish_time(item)
            url = item.get('link')
            title = item.get('title')

            if url is None:
                logger.warning(f'Source id "{self.__source.id}" has item without url in feed')
                continue

            if publish_time is None:
                logger.warning(f'Source id "{self.__source.id}" has item without publish time in feed')

            try:
                Target.objects.get_or_create(
                    defaults=({'publish_time': publish_time} if publish_time else {}),
                    source=self.__source,
                    title=title,
                    url=url,
                )
            except MultipleObjectsReturned:
                dup_targets = Target.objects.filter(
                    source=self.__source,
                    title=title,
                    url=url,
                )
                logger.error(f'Duplicate targets found (source {self.__source}) (title {title}) (url {url})\n{dup_targets}')

    def __extract_publish_time(self, item):
        publish_time_parsed = item.get('published_parsed')

        return dt.datetime.fromtimestamp(
            time.mktime(publish_time_parsed)
        ).astimezone(pytz.timezone('Europe/Kiev')) if publish_time_parsed else None

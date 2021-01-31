import logging
import datetime as dt
import time
import pytz

import feedparser

from manager.models import Target


logger = logging.getLogger(__name__)


class SourceParser:

    @staticmethod
    def parse(source):
        """
        Parses given source object and saves five last items from feed as Target elements to database
        :param source: source object
        :type source: manager.models.Source

        :raises urllib.error.URLError: connection issues
        :raises ValueError: Feed not found, invalid or empty
        """

        feed = feedparser.parse(source.url)

        items = feed.get('entries', [])[:5]

        if len(items) == 0:
            raise ValueError('Feed is not found, empty or improperly parsed')

        SourceParser.__save_to_db(source, items)

    @staticmethod
    def __save_to_db(source, items):

        for item in items:
            publish_time = SourceParser.__extract_publish_time(item)
            url = item.get('link')
            title = item.get('title')

            if url is None:
                logger.warning(f'Source id "{source.id}" has item without url in feed')
                continue

            if publish_time is None:
                logger.warning(f'Source id "{source.id}" has item without publish time in feed')

            Target.objects.get_or_create(
                source=source,
                title=title,
                url=url,
                **({'publish_time': publish_time} if publish_time else {})
            )

    @staticmethod
    def __extract_publish_time(item):
        publish_time_parsed = item.get('published_parsed')

        return dt.datetime.fromtimestamp(
            time.mktime(publish_time_parsed)
        ).astimezone(pytz.timezone('Europe/Kiev')) if publish_time_parsed else None

import logging
import urllib.error

from manager.models import Source
from manager.source_parser import SourceParser


logger = logging.getLogger(__name__)


def parse_sources():
    """
    Parses active sources for targets
    """
    sources = Source.objects.filter(is_active=True)

    for source in sources:
        parser = SourceParser(source)
        try:
            parser.parse()
            parser.save()

        except urllib.error.URLError:
            logger.error(f'Connection Error: Could not parse source with id "{source.id}" and url "{source.url}"')
            continue

        except ValueError:
            logger.warning(f'Feed is not found or empty (source.id: "{source.id}") (url: "{source.url}")')
            continue


def reset_remaining_traffic_for_sources():

    for source in Source.objects.all():
        source.remaining_traffic = source.limit
        # TODO: add update_fields to save calls
        source.save(update_fields=['remaining_traffic'])

import logging
import urllib.error

from django.db.models import F

from manager.models import Source, StaticTarget
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
    Source.objects.update(remaining_traffic=F('limit'))


def reset_traffic_for_static_targets():
    StaticTarget.objects.update(traffic=0)

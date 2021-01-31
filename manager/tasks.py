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
        try:
            SourceParser.parse(source)

        except urllib.error.URLError:
            logger.error(f'Connection Error: Could not parse source with id "{source.id}" and url "{source.url}"')
            continue

        except ValueError:
            logger.warning(f'Feed is not found or empty (source.id: "{source.id}") (url: "{source.url}")')
            continue
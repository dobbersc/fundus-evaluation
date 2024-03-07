import functools
from datetime import datetime
from typing import Any, Dict, List, Protocol

from fundus_evaluation.utils import normalize_whitespaces


class Scraper(Protocol):
    """Protocol for scraping functions. The function name should have the prefix 'scrape_'."""
    __name__: str

    def __call__(self, *, url: str, html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
        ...



def _normalize_whitespaces(scraper: Scraper) -> Scraper:
    """Decorator to normalize whitespaces for a Scraper callable."""

    @functools.wraps(scraper)
    def wrapper(*, url: str, html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
        return [
            normalize_whitespaces(paragraph)
            for paragraph in scraper(
                url=url, html=html, publisher_identifier=publisher_identifier, crawl_date=crawl_date
            )
        ]

    return wrapper


@_normalize_whitespaces
def scrape_newsplease(*, url: str, html: str, **_: Any) -> List[str]:
    import newsplease

    return newsplease.NewsPlease.from_html(html, url=url).maintext.split("\n")  # type: ignore[no-any-return]


@_normalize_whitespaces
def scrape_fundus(*, html: str, publisher_identifier: str, crawl_date: datetime, **_: Any) -> List[str]:
    from fundus import PublisherCollection
    from fundus.publishers.base_objects import PublisherEnum

    publisher: PublisherEnum = PublisherCollection[publisher_identifier]
    parsed_data: Dict[str, Any] = publisher.parser(crawl_date).parse(html, error_handling="raise")
    return list(parsed_data["body"].as_text_sequence())

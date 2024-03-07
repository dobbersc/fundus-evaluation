from datetime import datetime
from typing import Any, Dict, List, Protocol


class Extractor(Protocol):
    """Protocol for extraction functions."""
    __name__: str

    def __call__(self, *, url: str, html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
        ...


def extract_fundus(html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
    from fundus import PublisherCollection
    from fundus.publishers.base_objects import PublisherEnum

    publisher: PublisherEnum = PublisherCollection[publisher_identifier]
    parsed_data: Dict[str, Any] = publisher.parser(crawl_date).parse(html, error_handling="raise")
    return list(parsed_data["body"].as_text_sequence())

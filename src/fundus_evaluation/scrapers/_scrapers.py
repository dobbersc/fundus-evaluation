import functools
from datetime import datetime
from typing import Any, Dict, Iterator, List, Protocol, runtime_checkable

from fundus_evaluation.utils import normalize_whitespaces


@runtime_checkable
class Scraper(Protocol):
    """Protocol for scraping functions. The function name should have the prefix 'scrape_'."""

    __name__: str

    def __call__(self, *, url: str, html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
        ...


def normalize(scraper: Scraper) -> Scraper:
    """Decorator to normalize whitespaces and remove empty paragraphs for a Scraper callable."""

    @functools.wraps(scraper)
    def wrapper(*, url: str, html: str, publisher_identifier: str, crawl_date: datetime) -> List[str]:
        whitespace_normalized_paragraphs: Iterator[str] = (
            normalize_whitespaces(paragraph)
            for paragraph in scraper(
                url=url, html=html, publisher_identifier=publisher_identifier, crawl_date=crawl_date
            )
        )
        return [paragraph for paragraph in whitespace_normalized_paragraphs if paragraph]

    return wrapper


@normalize
def scrape_boilernet(*, html: str, **_: Any) -> List[str]:
    from fundus_evaluation.scrapers import boilernet

    body: str = boilernet.extract(html)
    return body.split("\n")


@normalize
def scrape_boilerpipe(*, html: str, **_: Any) -> List[str]:
    import boilerpipe.extract as boilerpipe

    extractor = boilerpipe.Extractor(extractor="ArticleExtractor", html=html)
    body: str = str(extractor.getText())
    return body.split("\n")


@normalize
def scrape_fundus(*, html: str, publisher_identifier: str, crawl_date: datetime, **_: Any) -> List[str]:
    from fundus import PublisherCollection
    from fundus.publishers import Publisher

    publisher: Publisher = PublisherCollection[publisher_identifier]
    parsed_data: Dict[str, Any] = publisher.parser(crawl_date).parse(html, error_handling="raise")
    return list(parsed_data["body"].as_text_sequence())


@normalize
def scrape_justext(*, html: str, **_: Any) -> List[str]:
    import justext

    # We use the same parameters as in the web-content-extraction-benchmark repository,
    # except that we include headings in our benchmark:
    # https://github.com/chatnoir-eu/web-content-extraction-benchmark/blob/221b6503d66bf4faa378e6ae3c3f63ee01d584c6/src/extraction_benchmark/extractors/extractors.py#L94
    justext_paragraphs = justext.justext(
        html,
        justext.get_stoplist("English"),
        length_low=50,
        length_high=200,
        stopwords_low=0.1,
        stopwords_high=0.2,
        max_link_density=0.2,
        max_heading_distance=200,
        no_headings=False,
        encoding="utf-8",
    )

    return [paragraph.text for paragraph in justext_paragraphs if not paragraph.is_boilerplate]


@normalize
def scrape_newsplease(*, url: str, html: str, **_: Any) -> List[str]:
    import newsplease

    body: str = newsplease.NewsPlease.from_html(html, url=url).maintext
    return body.split("\n")


@normalize
def scrape_trafilatura(*, html: str, **_: Any) -> List[str]:
    import trafilatura

    body: str = trafilatura.extract(html, include_tables=False, include_comments=False)
    return body.split("\n")


@normalize
def scrape_bte(*, html: str, **_: Any) -> List[str]:
    from fundus_evaluation.scrapers import bte

    body: str = bte.html2text(html)
    return body.split("\n")

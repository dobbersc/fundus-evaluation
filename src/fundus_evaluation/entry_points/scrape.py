import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, Set, Tuple, Union

from tqdm import tqdm

from fundus_evaluation import SCRAPERS
from fundus_evaluation.scrapers import Scraper
from fundus_evaluation.utils import (
    EvaluationArticle,
    load_evaluation_articles,
    load_zipped_html,
)


def _scrape_articles(
    scraper: Scraper, evaluation_articles: Dict[str, EvaluationArticle], html_directory: Path
) -> Iterator[Tuple[str, EvaluationArticle]]:
    for article_identifier, evaluation_article in evaluation_articles.items():
        url: str = evaluation_article["url"]
        html: str = load_zipped_html(html_directory / article_identifier)
        crawl_date: datetime = datetime.fromisoformat(evaluation_article["crawl_date"])
        publisher_identifier: str = article_identifier.split("_")[0]

        scraped_article: EvaluationArticle = {
            "url": url,
            "body": scraper(url=url, html=html, publisher_identifier=publisher_identifier, crawl_date=crawl_date),
            "crawl_date": evaluation_article["crawl_date"],
        }

        yield article_identifier, scraped_article


def scrape(
    ground_truth_path: Union[str, Path],
    html_directory: Union[str, Path],
    output_directory: Union[str, Path],
    scrapers: Union[Dict[str, Scraper], Set[str], None] = None,
) -> None:
    if scrapers is None:
        scrapers = SCRAPERS
    elif isinstance(scrapers, Set):
        scrapers = {
            scraper_identifier: scraper
            for scraper_identifier, scraper in SCRAPERS.items()
            if scraper_identifier in scrapers
        }

    html_directory = Path(html_directory)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    evaluation_articles: Dict[str, EvaluationArticle] = load_evaluation_articles(ground_truth_path)

    with tqdm(total=len(scrapers) * len(evaluation_articles), unit="Article") as progress_bar:
        for scraper_name, scraper in scrapers.items():
            progress_bar.set_description(f"Scraping with {scraper_name!r}")

            scraped_articles: Dict[str, EvaluationArticle] = {}
            for article_identifier, scraped_article in _scrape_articles(scraper, evaluation_articles, html_directory):
                scraped_articles[article_identifier] = scraped_article
                progress_bar.update()

            with (output_directory / f"{scraper_name}.json").open("w", encoding="utf-8") as output_file:
                json.dump(scraped_articles, output_file, indent=4, ensure_ascii=False)

import inspect
from typing import Final, Tuple

import fundus_evaluation
from fundus_evaluation.scrapers import Scraper

SCRAPER_PREFIX: Final[str] = "scrape_"
SCRAPERS: Tuple[Scraper, ...] = tuple(
    function
    for name, function in inspect.getmembers(fundus_evaluation.scrapers, inspect.isfunction)
    if name.startswith(SCRAPER_PREFIX)
)

import inspect
from typing import Dict, Final

import fundus_evaluation
from fundus_evaluation.scrapers import Scraper

__version__ = "1.0.0"

SCRAPER_PREFIX: Final[str] = "scrape_"
SCRAPERS: Dict[str, Scraper] = {
    name[len(SCRAPER_PREFIX) :]: function
    for name, function in inspect.getmembers(fundus_evaluation.scrapers, inspect.isfunction)
    if name.startswith(SCRAPER_PREFIX)
}

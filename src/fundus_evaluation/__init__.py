import inspect
from typing import Dict, Final

import fundus_evaluation
from fundus_evaluation.scorers import Scorer
from fundus_evaluation.scrapers import Scraper

__version__ = "1.0.0"

SCRAPER_PREFIX: Final[str] = "scrape_"
SCRAPERS: Dict[str, Scraper] = {
    name[len(SCRAPER_PREFIX) :]: function
    for name, function in inspect.getmembers(fundus_evaluation.scrapers, lambda x: isinstance(x, Scraper))
    if name.startswith(SCRAPER_PREFIX)
}

SCORER_PREFIX: Final[str] = "score_"
SCORERS: Dict[str, Scorer] = {
    name[len(SCORER_PREFIX) :]: function
    for name, function in inspect.getmembers(fundus_evaluation.scorers, lambda x: isinstance(x, Scorer))
    if name.startswith(SCORER_PREFIX)
}

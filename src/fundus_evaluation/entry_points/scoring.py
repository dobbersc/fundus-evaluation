import json
from pathlib import Path
from typing import Dict, Set, Union

from tqdm import tqdm

from fundus_evaluation import SCORERS
from fundus_evaluation.scorers import Scorer
from fundus_evaluation.utils import EvaluationArticle, load_evaluation_articles


def score(
    ground_truth_path: Union[str, Path],
    extractions_directory: Union[str, Path],
    output_path: Union[str, Path],
    scorers: Union[Dict[str, Scorer], Set[str], None] = None,
) -> None:
    if scorers is None:
        scorers = SCORERS
    elif isinstance(scorers, Set):
        scorers = {
            scorer_identifier: scorer for scorer_identifier, scorer in SCORERS.items() if scorer_identifier in scorers
        }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    reference_articles: Dict[str, EvaluationArticle] = load_evaluation_articles(ground_truth_path)
    scraper_to_hypothesis_articles: Dict[str, Dict[str, EvaluationArticle]] = {
        extraction_path.stem: load_evaluation_articles(extraction_path)
        for extraction_path in Path(extractions_directory).glob("*.json")
    }

    results: Dict[str, Dict[str, Dict[str, float]]] = {}

    with tqdm(total=len(scraper_to_hypothesis_articles) * len(scorers), unit="Score") as progress_bar:
        for scraper_identifier, hypothesis_articles in scraper_to_hypothesis_articles.items():
            scraper_results: Dict[str, Dict[str, float]] = {}
            for scorer_identifier, scorer in scorers.items():
                progress_bar.set_description(f"Evaluating {scraper_identifier!r} with {scorer_identifier!r}")
                scraper_results[scorer_identifier] = scorer(reference_articles, hypothesis_articles)
                progress_bar.update()

            results[scraper_identifier] = scraper_results

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=4, sort_keys=True, ensure_ascii=False)

from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import pandas as pd
from tqdm import tqdm

from fundus_evaluation import SCORERS
from fundus_evaluation.scorers import Scorer
from fundus_evaluation.utils import EvaluationArticle, load_evaluation_articles


def score(
    ground_truth_path: Union[str, Path],
    extractions_directory: Union[str, Path],
    output_directory: Union[str, Path],
    scorers: Union[Dict[str, Scorer], Set[str], None] = None,
    max_optional_paragraphs: Optional[int] = 4,
) -> None:
    if scorers is None:
        scorers = SCORERS
    elif isinstance(scorers, Set):
        scorers = {
            scorer_identifier: scorer for scorer_identifier, scorer in SCORERS.items() if scorer_identifier in scorers
        }

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    reference_articles: Dict[str, EvaluationArticle] = load_evaluation_articles(ground_truth_path)
    scraper_to_hypothesis_articles: Dict[str, Dict[str, EvaluationArticle]] = {
        extraction_path.stem: load_evaluation_articles(extraction_path)
        for extraction_path in Path(extractions_directory).glob("*.json")
    }

    with tqdm(total=len(scorers) * len(scraper_to_hypothesis_articles), unit="Score") as progress_bar:
        for scorer_identifier, scorer in scorers.items():
            results: List[pd.DataFrame] = []
            for scraper_identifier, hypothesis_articles in scraper_to_hypothesis_articles.items():
                progress_bar.set_description(f"Evaluating {scraper_identifier!r} with {scorer_identifier!r}")

                results.append(
                    scorer(reference_articles, hypothesis_articles, max_optional_paragraphs)
                    .assign(scraper=scraper_identifier)
                    .set_index("scraper", append=True)
                )
                progress_bar.update()

            combined_results: pd.DataFrame = pd.concat(results).reorder_levels(["scraper", "article"])
            combined_results.to_csv(output_directory / f"{scorer_identifier}.tsv", sep="\t")

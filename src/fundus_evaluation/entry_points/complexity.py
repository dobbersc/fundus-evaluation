from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

from fundus_evaluation.complexity import compute_dataset_complexities
from fundus_evaluation.utils import (
    EvaluationArticle,
    load_evaluation_articles,
    load_zipped_html,
)


def complexity(
    ground_truth_path: Union[str, Path],
    html_directory: Union[str, Path],
    output_path: Union[str, Path],
) -> None:
    html_directory = Path(html_directory)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    evaluation_articles: Dict[str, EvaluationArticle] = load_evaluation_articles(ground_truth_path)

    htmls: List[str] = [
        load_zipped_html(html_directory / article_identifier) for article_identifier in evaluation_articles
    ]
    bodies: List[List[str]] = [article["body"] for article in evaluation_articles.values()]

    df: pd.DataFrame = pd.DataFrame(
        {
            "complexity_without_optional_paragraphs": compute_dataset_complexities(
                htmls, bodies, include_optional_paragraphs=False
            ),
            "complexity_with_optional_paragraphs": compute_dataset_complexities(
                htmls, bodies, include_optional_paragraphs=True
            ),
        },
        index=pd.Index(evaluation_articles, name="article"),
    )
    df.sort_index().to_csv(output_path, sep="\t")

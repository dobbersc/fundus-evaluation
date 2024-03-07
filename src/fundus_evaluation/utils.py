import json
from pathlib import Path
from typing import TypedDict, List, Union, Dict


class EvaluationArticle(TypedDict):
    url: str
    body: List[str]  # List of paragraphs
    crawl_date: str


def load_evaluation_articles(path: Union[str, Path]) -> Dict[str, EvaluationArticle]:
    """Loads the evaluation articles from a JSON file.

    Args:
        path: The path to the JSON file containing the evaluation articles.

    Returns:
        A dictionary with article identifiers as keys and
        extraction content as EvaluationArticle dictionaries as values.
        The dictionary is sorted by their article identifier key.
    """
    with open(path, "r", encoding="utf-8") as f:
        return dict(sorted(json.load(f).items()))


def normalize_whitespaces(text: str) -> str:
    return " ".join(text.split())

import json
from pathlib import Path
from typing import (
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Union,
)

import more_itertools


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


def is_optional_paragraph(paragraph: str) -> bool:
    return paragraph[0] == "[" and paragraph[-1] == "]"


def remove_optional_paragraph_marker(paragraph: str) -> str:
    assert is_optional_paragraph(paragraph)
    return paragraph[1:-1]


def remove_optional_paragraphs(body: List[str], remove_indices: Set[int]) -> List[str]:
    return [
        remove_optional_paragraph_marker(paragraph) if is_optional_paragraph(paragraph) else paragraph
        for index, paragraph in enumerate(body)
        if index not in remove_indices
    ]


def get_reference_bodies(body: List[str], max_optional_paragraphs: Optional[int] = None) -> Iterator[List[str]]:
    optional_paragraph_indices: Tuple[int, ...] = tuple(
        index for index, paragraph in enumerate(body) if is_optional_paragraph(paragraph)
    )

    if len(optional_paragraph_indices) > max_optional_paragraphs:
        yield remove_optional_paragraphs(body, remove_indices=set())
        yield remove_optional_paragraphs(body, remove_indices=set(optional_paragraph_indices))
        return

    for remove_indices in more_itertools.powerset(optional_paragraph_indices):
        yield remove_optional_paragraphs(body, remove_indices=set(remove_indices))


def normalize_whitespaces(text: str) -> str:
    return " ".join(text.split())

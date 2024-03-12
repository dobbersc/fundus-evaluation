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


def load_zipped_html(path: Path) -> str:
    return gzip.decompress(path.read_bytes()).decode("utf-8")


def is_optional_paragraph(paragraph: str) -> bool:
    return paragraph[0] == "[" and paragraph[-1] == "]"


def remove_optional_paragraph_marker(paragraph: str) -> str:
    return paragraph[1:-1] if is_optional_paragraph(paragraph) else paragraph


def prepare_body(body: List[str], remove_paragraphs: AbstractSet[int] = frozenset()) -> List[str]:
    return [
        remove_optional_paragraph_marker(paragraph)
        for index, paragraph in enumerate(body)
        if index not in remove_paragraphs
    ]


def get_optional_paragraph_indices(body: List[str]) -> Tuple[int, ...]:
    return tuple(index for index, paragraph in enumerate(body) if is_optional_paragraph(paragraph))


def get_reference_bodies(body: List[str], max_optional_paragraphs: Optional[int] = None) -> Iterator[List[str]]:
    optional_paragraph_indices: Tuple[int, ...] = get_optional_paragraph_indices(body)

    if max_optional_paragraphs is not None and len(optional_paragraph_indices) > max_optional_paragraphs:
        yield prepare_body(body)
        yield prepare_body(body, remove_paragraphs=set(optional_paragraph_indices))
        return

    for remove_indices in more_itertools.powerset(optional_paragraph_indices):
        yield prepare_body(body, remove_paragraphs=set(remove_indices))


def normalize_whitespaces(text: str) -> str:
    return " ".join(text.split())

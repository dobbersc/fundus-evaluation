from typing import List, Sequence

from resiliparse.parse.html import HTMLTree

from fundus_evaluation.utils import (
    get_optional_paragraph_indices,
    prepare_body,
    tokenize_words,
)


def compute_complexity(html: str, text: str) -> float:
    """Calculates the HTML page complexity based on the pages extracted ground truth text.

    The page complexity 𝑐 is defined as
        𝑐 = 1 − |{𝑡 ∈ 𝑇 : truth(𝑡) = 1}| / |𝑇|,
    where 𝑇 is a multiset of DOM text tokens and truth(𝑡) returns 1 if token 𝑡 belongs to the ground truth.
    Negative scores resulting from a faulty ground truth
    with duplicated text or text not in the source HTML are clipped to zero.

    This variation of the page complexity has been defined by Bevendorff et al.
    in "An Empirical Comparison of Web Content Extraction Algorithms".
    Paper: https://downloads.webis.de/publications/papers/bevendorff_2023b.pdf

    Args:
        html: The HTML as string.
        text: The HTML's ground truth text.

    Returns:
        The page complexity.
    """
    num_ground_truth_tokens: int = len(tokenize_words(text))

    tree: HTMLTree = HTMLTree.parse(html)
    for e in tree.body.query_selector_all("script, style"):
        e.decompose()
    num_dom_text_tokens: int = len(tokenize_words(tree.body.text))

    complexity: float = 1 - num_ground_truth_tokens / num_dom_text_tokens
    return max(0.0, min(complexity, 1.0))  # Restrict score to [0; 1]


def compute_dataset_complexities(
    htmls: Sequence[str],
    bodies: Sequence[List[str]],
    include_optional_paragraphs: bool = False,
) -> List[float]:
    assert len(htmls) == len(bodies)
    return [
        compute_complexity(
            html=html,
            text=" ".join(
                prepare_body(body)
                if include_optional_paragraphs
                else prepare_body(body, remove_paragraphs=set(get_optional_paragraph_indices(body)))
            ),
        )
        for html, body in zip(htmls, bodies)
    ]

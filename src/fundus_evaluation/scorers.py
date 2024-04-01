import collections
import dataclasses
from typing import (
    Counter,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

import pandas as pd

from fundus_evaluation.utils import EvaluationArticle, get_reference_bodies

T = TypeVar("T")


@runtime_checkable
class Scorer(Protocol):
    """Protocol for scoring functions. The function name should have the prefix 'score_'.
    The function return value should be a pandas data frame with the index column "article"
    of article identifiers and the remaining columns for the respective article scores.
    """

    __name__: str

    def __call__(
        self,
        reference_articles: Dict[str, EvaluationArticle],
        hypothesis_articles: Dict[str, EvaluationArticle],
        max_optional_paragraphs: Optional[int] = None,
    ) -> pd.DataFrame: ...


@dataclasses.dataclass
class ConfusionMatrix:
    true_positives: int = 0
    true_negatives: int = 0  # The true negatives are not relevant in this task
    false_positives: int = 0
    false_negatives: int = 0

    @classmethod
    def from_evaluation(cls, reference: Iterable[T], hypothesis: Iterable[T]) -> "ConfusionMatrix":
        reference_counter: Counter[T] = collections.Counter(reference)
        hypothesis_counter: Counter[T] = collections.Counter(hypothesis)

        confusion_matrix: ConfusionMatrix = ConfusionMatrix()
        for key in reference_counter.keys() | hypothesis_counter.keys():
            reference_count: int = reference_counter.get(key, 0)
            hypothesis_count: int = hypothesis_counter.get(key, 0)

            confusion_matrix.true_positives += min(reference_count, hypothesis_count)
            confusion_matrix.false_positives += max(0, hypothesis_count - reference_count)
            confusion_matrix.false_negatives += max(0, reference_count - hypothesis_count)

        return confusion_matrix

    def precision(self) -> float:
        try:
            return self.true_positives / (self.true_positives + self.false_positives)
        except ZeroDivisionError:
            return float("NaN")

    def recall(self) -> float:
        try:
            return self.true_positives / (self.true_positives + self.false_negatives)
        except ZeroDivisionError:
            return float("NaN")

    def f1_score(self) -> float:
        precision: float = self.precision()
        recall: float = self.recall()
        try:
            return 2 * precision * recall / (precision + recall)
        except ZeroDivisionError:
            return float("NaN")


def score_paragraph_match(
    reference_articles: Dict[str, EvaluationArticle],
    hypothesis_articles: Dict[str, EvaluationArticle],
    max_optional_paragraphs: Optional[int] = None,
) -> pd.DataFrame:
    assert reference_articles.keys() == hypothesis_articles.keys()

    paragraph_scores: Dict[str, List[float]] = {"precision": [], "recall": [], "f1_score": []}
    for reference_article, hypothesis_article in zip(reference_articles.values(), hypothesis_articles.values()):
        reference_bodies: Iterator[List[str]] = get_reference_bodies(reference_article["body"], max_optional_paragraphs)
        hypothesis_body: List[str] = hypothesis_article["body"]

        confusion_matrix_candidates: Iterable[ConfusionMatrix] = (
            ConfusionMatrix.from_evaluation(reference_body, hypothesis_body) for reference_body in reference_bodies
        )
        best_confusion_matrix: ConfusionMatrix = max(confusion_matrix_candidates, key=lambda matrix: matrix.f1_score())

        paragraph_scores["precision"].append(best_confusion_matrix.precision())
        paragraph_scores["recall"].append(best_confusion_matrix.recall())
        paragraph_scores["f1_score"].append(best_confusion_matrix.f1_score())

    return pd.DataFrame(paragraph_scores, index=pd.Index(reference_articles, name="article"))


def score_wer(
    reference_articles: Dict[str, EvaluationArticle],
    hypothesis_articles: Dict[str, EvaluationArticle],
    max_optional_paragraphs: Optional[int] = None,
) -> pd.DataFrame:
    import jiwer

    assert reference_articles.keys() == hypothesis_articles.keys()

    word_error_rates: List[float] = []
    for reference_article, hypothesis_article in zip(reference_articles.values(), hypothesis_articles.values()):
        reference_bodies: List[str] = [
            "\n\n".join(body) for body in get_reference_bodies(reference_article["body"], max_optional_paragraphs)
        ]
        hypothesis_body: str = "\n\n".join(hypothesis_article["body"])

        candidate_word_error_rates: Iterator[float] = (
            jiwer.wer(reference_body, hypothesis_body) for reference_body in reference_bodies
        )
        word_error_rates.append(min(candidate_word_error_rates))

    return pd.DataFrame({"wer": word_error_rates}, index=pd.Index(reference_articles, name="article"))


def score_rouge_lsum(
    reference_articles: Dict[str, EvaluationArticle],
    hypothesis_articles: Dict[str, EvaluationArticle],
    max_optional_paragraphs: Optional[int] = None,
) -> pd.DataFrame:
    import nltk
    from rouge_score import rouge_scorer
    from rouge_score.scoring import Score

    assert reference_articles.keys() == hypothesis_articles.keys()

    # Download tokenizer required for ROUGE-LSum
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    rouge: rouge_scorer.RougeScorer = rouge_scorer.RougeScorer(["rougeLsum"], use_stemmer=False, split_summaries=True)

    rouge_scores: Dict[str, List[float]] = {"precision": [], "recall": [], "f1_score": []}
    for reference_article, hypothesis_article in zip(reference_articles.values(), hypothesis_articles.values()):
        reference_bodies: List[str] = [
            "\n\n".join(body) for body in get_reference_bodies(reference_article["body"], max_optional_paragraphs)
        ]
        hypothesis_body: str = "\n\n".join(hypothesis_article["body"])

        candidate_scores: Iterator[Score] = (
            rouge.score(reference_body, hypothesis_body)["rougeLsum"] for reference_body in reference_bodies
        )
        best_score: Score = max(candidate_scores, key=lambda score: score.fmeasure)

        rouge_scores["precision"].append(best_score.precision)
        rouge_scores["recall"].append(best_score.recall)
        rouge_scores["f1_score"].append(best_score.fmeasure)

    return pd.DataFrame(rouge_scores, index=pd.Index(reference_articles, name="article"))

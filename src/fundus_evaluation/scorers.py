import collections
import dataclasses
from typing import (
    Any,
    Counter,
    Dict,
    Iterable,
    Iterator,
    List,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from fundus_evaluation.utils import EvaluationArticle, get_reference_bodies

T = TypeVar("T")


@runtime_checkable
class Scorer(Protocol):
    """Protocol for scoring functions. The function name should have the prefix 'score_'."""

    __name__: str

    def __call__(
        self,
        reference_articles: Dict[str, EvaluationArticle],
        hypothesis_articles: Dict[str, EvaluationArticle],
        **kwargs: Any,
    ) -> Dict[str, float]:
        ...


@dataclasses.dataclass
class ConfusionMatrix:
    true_positives: int = 0
    # The true negatives are not relevant in this task.
    # TODO: But we could explicitly mark paragraphs / sections that we do not want to extract.
    #   This would have no impact on the Precision, Recall and F1-Scorer score but on the Accuracy.
    true_negatives: int = 0
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

    def __add__(self, other: "ConfusionMatrix") -> "ConfusionMatrix":
        return ConfusionMatrix(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
        )


@dataclasses.dataclass
class LevenshteinValues:
    hits: int = 0
    substitutions: int = 0
    deletions: int = 0
    insertions: int = 0

    def word_error_rate(self) -> float:
        s, d, i, h = (
            self.substitutions,
            self.deletions,
            self.insertions,
            self.hits,
        )
        return (s + d + i) / (h + s + d)


def score_paragraph_match(
    reference_articles: Dict[str, EvaluationArticle], hypothesis_articles: Dict[str, EvaluationArticle], **_: Any
) -> Dict[str, float]:
    confusion_matrix: ConfusionMatrix = ConfusionMatrix()
    for reference_article, hypothesis_article in zip(reference_articles.values(), hypothesis_articles.values()):
        reference_bodies: Iterator[List[str]] = get_reference_bodies(reference_article["body"])
        hypothesis_body: List[str] = hypothesis_article["body"]

        confusion_matrix_candidates: Iterable[ConfusionMatrix] = (
            ConfusionMatrix.from_evaluation(reference_body, hypothesis_body) for reference_body in reference_bodies
        )
        confusion_matrix += max(confusion_matrix_candidates, key=lambda matrix: matrix.f1_score())

    return {
        "precision": confusion_matrix.precision(),
        "recall": confusion_matrix.recall(),
        "f1_score": confusion_matrix.f1_score(),
    }


def score_wer(
    reference_articles: Dict[str, EvaluationArticle], hypothesis_articles: Dict[str, EvaluationArticle], **_: Any
) -> Dict[str, float]:
    import jiwer

    levenshtein_values: LevenshteinValues = LevenshteinValues()
    for reference_article, hypothesis_article in zip(reference_articles.values(), hypothesis_articles.values()):
        reference_bodies: List[str] = ["\n\n".join(body) for body in get_reference_bodies(reference_article["body"])]
        hypothesis_body: str = "\n\n".join(hypothesis_article["body"])

        candidate_word_outputs: Iterator[jiwer.WordOutput] = (
            jiwer.process_words(reference_body, hypothesis_body) for reference_body in reference_bodies
        )
        word_output: jiwer.WordOutput = min(candidate_word_outputs, key=lambda output: output.wer)

        levenshtein_values.hits += word_output.hits
        levenshtein_values.substitutions += word_output.substitutions
        levenshtein_values.deletions += word_output.deletions
        levenshtein_values.insertions += word_output.insertions

    return {"wer": levenshtein_values.word_error_rate()}

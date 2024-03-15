import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# Set plot theme
sns.set_theme(style="whitegrid", palette="muted")


def draw_complexity_boxplot(complexity: pd.DataFrame, out: Union[str, Path, None] = None) -> None:
    complexity = complexity.rename(
        columns={
            "complexity_with_optional_paragraphs": "With Optional\nParagraphs",
            "complexity_without_optional_paragraphs": "Without Optional\nParagraphs",
        }
    ).sort_index(axis=1)

    facet_grid: sns.FacetGrid = sns.catplot(
        complexity.melt(["article"], var_name="complexity_type", value_name="complexity_value"),
        x="complexity_type",
        y="complexity_value",
        kind="box",
        width=0.25,
    )

    for patch in facet_grid.ax.patches:
        r, g, b, _ = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0.7))

    facet_grid.set_xlabels("")
    facet_grid.set_ylabels("Complexity")
    facet_grid.set(ylim=(0, 1))

    plt.tight_layout()

    if out is None:
        plt.show()
    else:
        plt.savefig(Path(out) / "complexity.pdf", dpi=300)


def draw_rouge_lsum_stripplot(rouge_lsum: pd.DataFrame, out: Union[str, Path, None] = None) -> None:
    np.random.seed(1)

    rouge_lsum = rouge_lsum.rename(
        columns={
            "precision": "Precision",
            "recall": "Recall",
            "f1_score": "F1-Score",
        }
    ).replace(
        {
            "boilernet": "BoilerNet",
            "boilerpipe": "Boilerpipe",
            "bte": "BTE",
            "fundus": "Fundus",
            "justext": "jusText",
            "newsplease": "news-please",
            "trafilatura": "Trafilatura",
        }
    )

    facet_grid: sns.FacetGrid = sns.catplot(
        rouge_lsum.melt(["scraper", "article"], var_name="Variant", value_name="ROUGE-LSum"),
        x="scraper",
        y="ROUGE-LSum",
        col="Variant",
        kind="strip",
        alpha=0.4,
        order=rouge_lsum.groupby("scraper")["F1-Score"].mean().sort_values(ascending=False).index,
    )

    facet_grid.set_xticklabels(rotation=45)
    facet_grid.set_xlabels("")
    facet_grid.set(ylim=(0, 1))

    plt.tight_layout()

    if out is None:
        plt.show()
    else:
        plt.savefig(Path(out) / "rouge_lsum_stripplot.pdf", dpi=300)


def draw_rouge_lsum_f1_score_stripplot(rouge_lsum: pd.DataFrame, out: Union[str, Path, None] = None) -> None:
    np.random.seed(1)

    rouge_lsum = rouge_lsum.replace(
        {
            "boilernet": "BoilerNet",
            "boilerpipe": "Boilerpipe",
            "bte": "BTE",
            "fundus": "Fundus",
            "justext": "jusText",
            "newsplease": "news-please",
            "trafilatura": "Trafilatura",
        }
    )

    facet_grid: sns.FacetGrid = sns.catplot(
        rouge_lsum[["scraper", "article", "f1_score"]],
        x="scraper",
        y="f1_score",
        kind="strip",
        alpha=0.4,
        order=rouge_lsum.groupby("scraper")["f1_score"].mean().sort_values(ascending=False).index,
    )

    facet_grid.set_xticklabels(rotation=45)
    facet_grid.set_xlabels("")
    facet_grid.set_ylabels("ROUGE-LSum F1-Score")
    facet_grid.set(ylim=(0, 1))

    plt.tight_layout()

    if out is None:
        plt.show()
    else:
        plt.savefig(Path(out) / "rouge_lsum_stripplot_f1_score.pdf", dpi=300)


def compute_rouge_lsum_scraper_summary(rouge_lsum: pd.DataFrame, out: Union[str, Path, None] = None) -> pd.DataFrame:
    if rouge_lsum.isna().any(axis=None):
        warnings.warn("NaN Values Detected!")

    summary: pd.DataFrame = (
        rouge_lsum.set_index(["scraper", "article"])
        .groupby("scraper")
        .agg(["mean", "std"])
        .mul(100)
        .round(2)
        .sort_values(("f1_score", "mean"), ascending=False)
    )

    if out:
        summary.to_csv(Path(out) / "rouge_lsum_scraper_summary.tsv", sep="\t")
    return summary


def compute_rouge_lsum_scraper_to_publisher_summary(
    rouge_lsum: pd.DataFrame, out: Union[str, Path, None] = None
) -> pd.DataFrame:
    if rouge_lsum.isna().any(axis=None):
        warnings.warn("NaN Values Detected!")

    summary = (
        rouge_lsum.assign(publisher=rouge_lsum["article"].str.replace("_\d+\.html\.gz", "", regex=True))[
            ["scraper", "publisher", "precision", "recall", "f1_score"]
        ]
        .set_index(["scraper", "publisher"])
        .groupby(["scraper", "publisher"])
        .agg(["mean", "std"])
        .mul(100)
        .round(2)
        .sort_values(["scraper", "publisher"], ascending=False)
    )

    if out:
        summary.to_csv(Path(out) / "rouge_lsum_summary.tsv", sep="\t")
    return summary

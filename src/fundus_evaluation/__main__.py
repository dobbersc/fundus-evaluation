import argparse
import sys
from pathlib import Path
from typing import Any, List, Optional

import fundus_evaluation


class RawTextArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass


def none_or_int(value: str) -> Optional[int]:
    return None if value == "None" else int(value)


def call_complexity(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.complexity import complexity

    complexity(
        ground_truth_path=args.ground_truth_path,
        html_directory=args.html_directory,
        output_path=args.output_path,
    )


def call_scrape(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.scrape import scrape

    scrape(
        ground_truth_path=args.ground_truth_path,
        html_directory=args.html_directory,
        output_directory=args.output_directory,
        scrapers=None if args.scrapers is None else set(args.scrapers),
        exclude_scrapers=set(args.exclude_scrapers),
    )


def call_score(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.score import score

    score(
        ground_truth_path=args.ground_truth_path,
        extractions_directory=args.extractions_directory,
        output_directory=args.output_directory,
        scorers=None if args.scorers is None else set(args.scorers),
        max_optional_paragraphs=args.max_optional_paragraphs,
    )


def call_analysis(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.analysis import analysis

    analysis(
        output_directory=args.output_directory,
        complexity_path=args.complexity_path,
        rouge_lsum_path=args.rouge_lsum_path,
    )


def add_complexity(subparsers: Any) -> None:
    scrape = subparsers.add_parser(
        "complexity",
        help="calculate page complexity scores",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    scrape.set_defaults(func=call_complexity)

    scrape.add_argument(
        "-t",
        "--ground-truth-path",
        type=Path,
        required=True,
        help="path to the dataset's ground truth file",
    )
    scrape.add_argument(
        "-d",
        "--html-directory",
        type=Path,
        required=True,
        help=(
            "path to dataset's HTML directory containing compressed HTML files "
            "corresponding to ground truth article extractions"
        ),
    )
    scrape.add_argument(
        "-o",
        "--output-path",
        type=Path,
        required=True,
        help="path to save the complexity scores as TSV",
    )


def add_scrape(subparsers: Any) -> None:
    scrape = subparsers.add_parser(
        "scrape",
        help="scrape extractions on the evaluation dataset",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    scrape.set_defaults(func=call_scrape)

    scrape.add_argument(
        "-t",
        "--ground-truth-path",
        type=Path,
        required=True,
        help="path to the dataset's ground truth file",
    )
    scrape.add_argument(
        "-d",
        "--html-directory",
        type=Path,
        required=True,
        help=(
            "path to dataset's HTML directory containing compressed HTML files "
            "corresponding to ground truth article extractions"
        ),
    )
    scrape.add_argument(
        "-o",
        "--output-directory",
        type=Path,
        required=True,
        help="directory to save the scrapers extractions as <scraper_name>.json",
    )
    scrape.add_argument(
        "-s",
        "--scrapers",
        nargs="+",
        choices=fundus_evaluation.SCRAPERS.keys(),
        default=None,
        help="effective scrapers for the evaluation; per default, all available scrapers will be included",
    )
    scrape.add_argument(
        "-e",
        "--exclude-scrapers",
        nargs="+",
        choices=fundus_evaluation.SCRAPERS.keys(),
        default=set(),
        help="excluded scrapers from the evaluation; per default, no scrapers will be excluded",
    )


def add_score(subparsers: Any) -> None:
    score = subparsers.add_parser(
        "score",
        help="calculate evaluation scores",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    score.set_defaults(func=call_score)

    score.add_argument(
        "-t",
        "--ground-truth-path",
        type=Path,
        required=True,
        help="path to the dataset's ground truth file",
    )
    score.add_argument(
        "-e",
        "--extractions-directory",
        type=Path,
        required=True,
        help="directory of the scraper's extractions, e.g. obtained from the 'scrape' entry point",
    )
    score.add_argument(
        "-o",
        "--output-directory",
        type=Path,
        required=True,
        help="directory to save the evaluation scores as <scorer_name>.tsv",
    )
    score.add_argument(
        "-s",
        "--scorers",
        nargs="+",
        choices=fundus_evaluation.SCORERS.keys(),
        default=None,
        help="effective scorers for the evaluation; per default, all available scorers will be included",
    )
    score.add_argument(
        "-p",
        "--max-optional-paragraphs",
        type=none_or_int,
        default=4,
        help="maximum number of variants of optional paragraphs from its powerset to include in the score calculation",
    )


def add_analysis(subparsers: Any) -> None:
    score = subparsers.add_parser(
        "analysis",
        help="generate tables and plots",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    score.set_defaults(func=call_analysis)

    score.add_argument(
        "-o",
        "--output-directory",
        type=Path,
        required=True,
        help="directory to save the analysis results",
    )
    score.add_argument(
        "-c",
        "--complexity-path",
        type=Path,
        default=None,
        help="path to calculated complexity scores as TSV",
    )
    score.add_argument(
        "-r",
        "--rouge-lsum-path",
        type=Path,
        default=None,
        help="path to calculated ROUGE-LSum scores as TSV",
    )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=RawTextArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {fundus_evaluation.__version__}")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="Fundus News Scraper Evaluation",
        description="select evaluation pipeline step",
    )
    add_complexity(subparsers)
    add_scrape(subparsers)
    add_score(subparsers)
    add_analysis(subparsers)

    return parser.parse_args(argv)


def run(argv: List[str]) -> None:
    """Parses the args and calls the dedicated function."""
    args: argparse.Namespace = parse_args(argv)
    args.func(args)


def main() -> None:
    """The main entry-point."""
    run(sys.argv[1:])


if __name__ == "__main__":
    main()

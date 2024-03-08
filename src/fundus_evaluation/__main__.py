import argparse
import sys
from pathlib import Path
from typing import Any, List

import fundus_evaluation


class RawTextArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass


def call_scrape(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.scraping import scrape

    scrape(
        ground_truth_path=args.ground_truth_path,
        html_directory=args.html_directory,
        output_directory=args.output_directory,
        scrapers=None if args.scrapers is None else set(args.scrapers),
    )


def call_score(args: argparse.Namespace) -> None:
    from fundus_evaluation.entry_points.scoring import score

    score(
        ground_truth_path=args.ground_truth_path,
        extractions_directory=args.extractions_directory,
        output_directory=args.output_directory,
        scorers=None if args.scorers is None else set(args.scorers),
    )


def add_scrape(subparsers: Any) -> None:
    scrape = subparsers.add_parser(
        "scrape",
        help="TODO",
        description="TODO",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    scrape.set_defaults(func=call_scrape)

    scrape.add_argument("-t", "--ground-truth-path", type=Path, required=True, help="TODO")
    scrape.add_argument("-d", "--html-directory", type=Path, required=True, help="TODO")
    scrape.add_argument("-o", "--output-directory", type=Path, required=True, help="TODO")
    scrape.add_argument(
        "-s", "--scrapers", nargs="+", choices=fundus_evaluation.SCRAPERS.keys(), default=None, help="TODO"
    )


def add_score(subparsers: Any) -> None:
    score = subparsers.add_parser(
        "score",
        help="TODO",
        description="TODO",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    score.set_defaults(func=call_score)

    score.add_argument("-t", "--ground-truth-path", type=Path, required=True, help="TODO")
    score.add_argument("-e", "--extractions-directory", type=Path, required=True, help="TODO")
    score.add_argument("-o", "--output-directory", type=Path, required=True, help="TODO")
    score.add_argument(
        "-s", "--scorers", nargs="+", choices=fundus_evaluation.SCORERS.keys(), default=None, help="TODO"
    )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=RawTextArgumentDefaultsHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {fundus_evaluation.__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    add_scrape(subparsers)
    add_score(subparsers)

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

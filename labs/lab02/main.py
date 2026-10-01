import argparse
import logging
import sys
from pathlib import Path

from shared.student import VARIANT_NUMBER

from .task1 import run_demo
from .task2 import run_analysis

LOGGER = logging.getLogger(__name__)


def positive_int(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Потрібне ціле число") from error

    if number <= 0:
        raise argparse.ArgumentTypeError("Число має бути більше нуля")

    return number


def main():
    parser = argparse.ArgumentParser(description="Лабораторна робота №2")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("demo", help="Демонстрація ООП")

    analyze = commands.add_parser("analyze", help="Аналіз словника паролів")
    analyze.add_argument("--wordlist", type=Path, required=True)
    analyze.add_argument("--min-length", type=positive_int, default=8)
    analyze.add_argument("--top-masks", type=positive_int, default=5)
    analyze.add_argument("--output-stats", type=Path, required=True)

    arguments = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        stream=sys.stdout,
    )

    if VARIANT_NUMBER != 6:
        LOGGER.error("Ця програма реалізована для варіанта 6")
        return 1

    try:
        if arguments.command == "demo":
            run_demo()
        else:
            run_analysis(
                arguments.wordlist,
                arguments.min_length,
                arguments.top_masks,
                arguments.output_stats,
            )
    except (OSError, UnicodeError, ValueError) as error:
        LOGGER.error("%s", error)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
import argparse

from letterboxd_solver import (
    generate_random_test_cases,
    read_word_list,
    test_solver,
    test_spell_bee_solver,
)


def main():
    word_list = read_word_list(
        "/Users/dhruvcharan/Desktop/dsa/12dicts-6.0.2/American/2of12.txt"
    )

    parser = argparse.ArgumentParser(
        description=(
            "Solve NYTimes Letterboxd or Spell Bee puzzles.\n\n"
            "Examples:\n"
            "  python main.py --puzzle letterboxd --input TIAUWLDBYRMO\n"
            "  python main.py --puzzle spellbee --input MAWRING\n"
            "  python main.py --puzzle letterboxd --random --max-iters 100\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--puzzle",
        choices=["letterboxd", "spellbee"],
        required=True,
        help=(
            "Type of puzzle to solve:\n"
            "  - 'letterboxd': Solve the Letterboxd puzzle.\n"
            "  - 'spellbee': Solve the Spell Bee puzzle."
        ),
    )
    parser.add_argument(
        "--input",
        required=False,
        help=(
            "Puzzle input:\n"
            "  - For Letterboxd: 12 letters forming 4 sides (e.g., TIAUWLDBYRMO).\n"
            "  - For Spell Bee: Center letter first, followed by other letters (e.g., MAWRING)."
        ),
    )
    parser.add_argument(
        "--max-path",
        type=int,
        default=3,
        help="Maximum path length for Letterboxd solutions (default: 3).",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate random test cases for Letterboxd.",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        default=50,
        help="Maximum iterations for random test cases (default: 50).",
    )

    args = parser.parse_args()

    if args.puzzle == "letterboxd" and not args.random:
        if not args.input:
            parser.error(
                "The --input argument is required for Letterboxd unless --random is specified."
            )
        if len(args.input) != 12:
            parser.error("Error: Letterboxd input must have exactly 12 letters.")

    if args.puzzle == "spellbee" and args.input:
        if len(args.input) < 7:
            parser.error(
                "Error: Spell Bee input must have at least 7 letters (center letter + 6 others)."
            )
    if args.random:
        generate_random_test_cases(max_iters=args.max_iters, word_list=word_list)
    elif args.puzzle == "letterboxd":
        test_solver(word_list=word_list, todays_word=args.input.upper())
    elif args.puzzle == "spellbee":
        test_spell_bee_solver(word_list=word_list, todays_word=args.input.upper())


if __name__ == "__main__":
    main()

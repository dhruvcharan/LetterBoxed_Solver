import argparse
from letterboxd_solver import GraphLetterBoxedSolver, generate_random_box_edges,read_word_list,SpellBeeSolver,test_solver,test_spell_bee_solver,generate_random_test_cases

def main():
    
    word_list = read_word_list(
    "/Users/dhruvcharan/Desktop/dsa/12dicts-6.0.2/American/2of12.txt"
    )

    parser = argparse.ArgumentParser(
        description="Solve Letterboxd or Spell Bee puzzles"
    )
    parser.add_argument(
        "--puzzle",
        choices=["letterboxd", "spellbee"],
        required=True,
        help="Type of puzzle to solve",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="For Letterboxd: 12 letters forming 4 sides (e.g., TIAUWLDBYRMO). "
        + "For Spell Bee: center letter first, followed by other letters (e.g., MAWRING)",
    )
    parser.add_argument(
        "--max-path",
        type=int,
        default=3,
        help="Maximum path length for Letterboxd solutions (default: 2)",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate random test cases for Letterboxd",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        default=50,
        help="Maximum iterations for random test cases (default: 50)",
    )

    args = parser.parse_args()

    if args.random:
        generate_random_test_cases(max_iters=args.max_iters,word_list=word_list)
    elif args.puzzle == "letterboxd":
        if len(args.input) != 12:
            print("Error: Letterboxd input must have exactly 12 letters")
            parser.print_help()
            exit(1)
        test_solver(args.input.upper())
    elif args.puzzle == "spellbee":
        test_spell_bee_solver(args.input.upper())



if __name__ == "__main__":
    main()

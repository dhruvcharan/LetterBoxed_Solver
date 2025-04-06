"""Flask Serve Endpoint"""

import os

from flask import Flask, render_template, request

from letterboxd_solver import GraphLetterBoxedSolver, SpellBeeSolver, read_word_list

app = Flask(__name__, static_folder="static", template_folder="templates")
WORD_LIST_PATH = os.path.join("word_lists", "2of12.txt")
word_list = read_word_list(WORD_LIST_PATH)


def sort_letterboxed_solutions(solutions):
    """
    Sort letterboxed results by:
    - Fewest words first
    - Then by most letters used
    """
    return sorted(solutions, key=lambda chain: (len(chain), -len(set("".join(chain)))))


@app.route("/", methods=["GET", "POST"])
def index():
    """Flask routing setup"""
    if request.method == "POST":
        game_type = request.form["game_type"]
        letters_input = request.form.get("letters", "").upper().strip()
        max_path = int(request.form.get("max_path", 3))
        is_random = request.form.get("random") == "on"
        # max_iters = int(request.form.get("max_iters", 50))

        if game_type == "letterboxed":
            if is_random:
                return render_template(
                    "index.html", error="Random Not Supported Just Yet"
                )

            if len(letters_input) != 12:
                return render_template(
                    "index.html",
                    error="Letter Boxed requires exactly 12 letters.",
                )

            box_edges = [list(letters_input[i : i + 3]) for i in range(0, 12, 3)]
            solver = GraphLetterBoxedSolver(
                word_list, box_edges, max_path_length=max_path
            )
            raw_solutions = solver.solve_bfs()
            sorted_solutions = sort_letterboxed_solutions(raw_solutions)
            return render_template(
                "result.html", game="Letter Boxed", solutions=sorted_solutions
            )

        if game_type == "spellbee":
            if len(letters_input) < 7:
                return render_template(
                    "index.html",
                    error="Spell Bee input must be at least 7 letters (center + 6).",
                )
            solver = SpellBeeSolver(word_list, list(letters_input))
            scored_words = solver.solve()
            return render_template(
                "result.html", game="Spelling Bee", solutions=scored_words
            )

    return render_template("index.html")


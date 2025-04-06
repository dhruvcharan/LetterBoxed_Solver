"""Flask Serve Endpoint"""
import os
import time
import logging
from flask import Flask, render_template, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

try:
    from letterboxd_solver import GraphLetterBoxedSolver, SpellBeeSolver, read_word_list
except ImportError as e:
    logger.critical(f"Failed to import required modules: {e}")
    raise

app = Flask(__name__, static_folder="static", template_folder="templates")

WORD_LIST_PATH = os.path.join("word_lists", "2of12.txt")
DEFAULT_MAX_PATH = 3
SOLVER_TIMEOUT = 60  # seconds

try:
    word_list = read_word_list(WORD_LIST_PATH)
    logger.info(f"Successfully loaded word list with {len(word_list)} words")
except Exception as e:
    logger.critical(f"Failed to load word list: {e}")
    word_list = []  # Empty fallback to prevent app from crashing


def sort_letterboxed_solutions(solutions):
    """
    Sort letterboxed results by:
    - Fewest words first
    - Then by most letters used
    """
    return sorted(solutions, key=lambda chain: (len(chain), -len(set("".join(chain)))))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('error.html', error="Internal server error"), 500


@app.route("/", methods=["GET", "POST"])
def index():
    """Flask routing setup with improved error handling"""
    if request.method != "POST":
        return render_template("index.html")
        
    try:
        game_type = request.form.get("game_type", "")
        if not game_type:
            return render_template("index.html", error="Game type is required")
            
        letters_input = request.form.get("letters", "").upper().strip()
        if not letters_input:
            return render_template("index.html", error="Letters input is required")
            
        try:
            max_path = int(request.form.get("max_path", DEFAULT_MAX_PATH))
            if max_path <= 0 or max_path > 10:  
                max_path = DEFAULT_MAX_PATH
                logger.warning(f"Invalid max_path value, using default: {DEFAULT_MAX_PATH}")
        except ValueError:
            max_path = DEFAULT_MAX_PATH
            logger.warning(f"Non-integer max_path value, using default: {DEFAULT_MAX_PATH}")
            
        is_random = request.form.get("random") == "on"
        
        if not word_list:
            return render_template("index.html", error="Word list is not available. Please try again later.")
        
        if game_type == "letterboxed":
            return handle_letterboxed(letters_input, max_path, is_random)
        elif game_type == "spellbee":
            return handle_spellbee(letters_input)
        else:
            return render_template("index.html", error=f"Unknown game type: {game_type}")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return render_template("index.html", error="An unexpected error occurred. Please try again.")


def handle_letterboxed(letters_input, max_path, is_random):
    """Handle Letter Boxed game with error handling"""
    if len(letters_input) != 12:
        return render_template(
            "index.html",
            error="Letter Boxed requires exactly 12 letters.",
        )
        
    if is_random:
        return render_template(
            "index.html", 
            error="Random Not Supported Just Yet"
        )
    
    try:
        box_edges = [list(letters_input[i : i + 3]) for i in range(0, 12, 3)]
        
        solver = GraphLetterBoxedSolver(
            word_list, box_edges, max_path_length=max_path
        )
        
        start_time = time.time()
        raw_solutions = solver.solve_bfs()
        solve_time = time.time() - start_time
        
        logger.info(f"Letterboxed solve completed in {solve_time:.2f}s with {len(raw_solutions)} solutions")
        
        if solve_time > SOLVER_TIMEOUT:
            logger.warning(f"Solve operation took {solve_time:.2f}s, exceeding recommended timeout")
        
        if not raw_solutions:
            return render_template(
                "index.html",
                error=f"No solutions found. Try increasing the maximum path length beyond {max_path}.",
            )
            
        sorted_solutions = sort_letterboxed_solutions(raw_solutions)
        if len(sorted_solutions) > 1000:  # Arbitrary limit
            logger.info(f"Trimming results from {len(sorted_solutions)} to 1000")
            sorted_solutions = sorted_solutions[:1000]
            
        return render_template(
            "result.html", 
            game="Letter Boxed", 
            solutions=sorted_solutions,
            solve_time=f"{solve_time:.2f}"
        )
        
    except MemoryError:
        logger.error("Memory error during letterboxed solve")
        return render_template(
            "index.html",
            error="The puzzle was too complex to solve with available memory. Try reducing the maximum path length."
        )
    except Exception as e:
        logger.error(f"Error solving letterboxed: {str(e)}")
        return render_template(
            "index.html",
            error="An error occurred while solving. Please try different parameters."
        )


def handle_spellbee(letters_input):
    """Handle Spell Bee game with error handling"""
    if len(letters_input) < 7:
        return render_template(
            "index.html",
            error="Spell Bee input must be at least 7 letters (center + 6).",
        )
    
    try:
        start_time = time.time()
        solver = SpellBeeSolver(word_list, list(letters_input))
        scored_words = solver.solve()
        solve_time = time.time() - start_time
        
        # Log performance
        logger.info(f"SpellBee solve completed in {solve_time:.2f}s with {len(scored_words)} words")
        
        if not scored_words:
            return render_template(
                "index.html",
                error="No valid words found for these letters."
            )
            
        return render_template(
            "result.html", 
            game="Spelling Bee", 
            solutions=scored_words,
            solve_time=f"{solve_time:.2f}"
        )
        
    except Exception as e:
        logger.error(f"Error solving spellbee: {str(e)}")
        return render_template(
            "index.html",
            error="An error occurred while solving. Please check your input."
        )


if __name__ == "__main__":
    if not os.path.exists(os.path.join(app.template_folder, "error.html")):
        logger.warning("error.html template missing, errors will not display properly")
        
    app.run(debug=False, host="0.0.0.0",port = 5001)
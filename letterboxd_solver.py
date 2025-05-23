"""A Class to Solve the NYTimes LetterBoxd and SpellBee Puzzles"""  # %%

import random
import string
from collections import defaultdict, deque
import time

import logging
import matplotlib.pyplot as plt
import networkx as nx


def read_word_list(filename):
    """Read the word list"""
    with open(filename, encoding="UTF-8") as f:
        return [line.strip().upper() for line in f]


def is_valid_word(word, box_edges):
    """
    Check if a word is valid according to the Letter Boxed rules.
    Specifically, check that no two consecutive letters are on the same edge.
    """
    available_letters = {letter for edge in box_edges for letter in edge}
    if not set(word).issubset(available_letters):
        return False

    # Create a map of which edge each letter belongs to
    letter_to_edge = {}
    for i, edge in enumerate(box_edges):
        for letter in edge:
            letter_to_edge[letter] = i

    for i in range(len(word) - 1):
        if letter_to_edge.get(word[i]) == letter_to_edge.get(word[i + 1]):
            return False

    return True


def filter_valid_words(list_of_words, box_edges):
    """
    Filters the word list to include only valid words that can be formed
    according to the Letter Boxed rules.
    """
    return [word for word in list_of_words if is_valid_word(word, box_edges)]


class GraphLetterBoxedSolver:
    """
    Graph Based Solver Class for the NYTimes LetterBoxd Puzzle
    """

    def __init__(self, list_of_words, box_edges, max_path_length=2):
        self.cleaned_word_list = [
            word.replace("-", "").replace(" ", "").replace("'", "")
            for word in list_of_words
        ]
        # Filter the word list to include only valid words
        self.valid_words = filter_valid_words(
            self.cleaned_word_list, box_edges)
        random.shuffle(self.valid_words)
        self.graph = self._build_graph(self.valid_words)
        self.letters = set(
            letter for word in self.valid_words for letter in word)
        self.max_path_length = max_path_length
        # print("box_edges:", box_edges)

    def _build_graph(self, list_of_words):
        """
        Build a graph where each word is a node and there's an
        edge if one word can transition to another.
        """
        graph = defaultdict(list)
        for word1 in list_of_words:
            for word2 in list_of_words:
                if word1 != word2 and word1[-1] == word2[0]:
                    graph[word1].append(word2)
        return graph

    def generate_dot_file(self, filename="graph.dot"):
        """
        Generate a .dot file for the graph.
        """
        with open(filename, "w", encoding="UTF-8") as f:
            f.write("digraph G {\n")
            for word, connections in self.graph.items():
                for connected_word in connections:
                    f.write(f'    "{word}" -> "{connected_word}";\n')
            f.write("}\n")
        print(f"Graph written to {filename}")

    def visualize_graph(self):
        """
        Visualize Graph using the networkx module
        """
        graph_object = nx.DiGraph()  # Create a directed graph
        for word, connections in self.graph.items():
            for connected_word in connections:
                graph_object.add_edge(word, connected_word)

        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(graph_object)
        nx.draw(
            graph_object,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            arrows=True,
            arrowstyle="->",
            arrowsize=20,
        )
        plt.title("Word Transition Graph")
        plt.show()

    def _all_letters_used(self, used_letters):
        return used_letters == self.letters

    def _dfs(self, current_word, used_letters, current_chain, visited=None, solution_fingerprints=None,
             start_time=None, iterations=0):
        """Perform the DFS on the current graph based on the present state with improved resilience"""
        if visited is None:
            visited = set()
        if solution_fingerprints is None:
            solution_fingerprints = set()
        if start_time is None:
            start_time = time.time()

        max_iterations = 1000000
        time_limit = 30  # seconds

        iterations += 1
        if iterations > max_iterations:
            logging.warning(
                f"DFS reached iteration limit for word: {current_word}")
            return []

        if iterations % 1000 == 0 and time.time() - start_time > time_limit:
            logging.warning(
                f"DFS timed out after {time_limit} seconds for word: {current_chain[0]}")
            return []

        if len(current_chain) > self.max_path_length:
            return []

        if self._all_letters_used(used_letters):
            solution_set = frozenset(current_chain)
            if solution_set not in solution_fingerprints:
                solution_fingerprints.add(solution_set)
                return [tuple(current_chain)]
            return []

        state_key = (current_word, frozenset(used_letters))
        if state_key in visited:
            return []
        visited.add(state_key)

        all_solutions = []

        try:
            next_words = self.graph.get(current_word, [])

            for next_word in next_words:
                new_letters = set(next_word) - used_letters
                if new_letters or not used_letters & set(next_word):
                    new_used_letters = used_letters | set(next_word)
                    result = self._dfs(
                        next_word,
                        new_used_letters,
                        current_chain + [next_word],
                        visited.copy(), 
                        solution_fingerprints,
                        start_time,
                        iterations
                    )
                    all_solutions.extend(result)

                    if len(all_solutions) > 1000:  
                        logging.info(
                            f"Found {len(all_solutions)} solutions in DFS branch, stopping early")
                        break

        except Exception as e:
            logging.error(f"Error in DFS for chain {current_chain}: {str(e)}")

        return all_solutions

    def solve(self):
        """Solve the given Class with improved resilience"""
        if not hasattr(self, 'valid_words') or not self.valid_words:
            logging.error("No valid words available")
            return set()

        if not hasattr(self, 'graph') or not self.graph:
            logging.error("Word graph not initialized")
            return set()

        if not isinstance(self.max_path_length, int) or self.max_path_length <= 0:
            logging.warning(
                f"Invalid max_path_length: {self.max_path_length}, using default of 10")
            self.max_path_length = 10

        unique_solutions = []
        solution_fingerprints = set()
        total_words = len(self.valid_words)

        progress_interval = max(1, total_words // 10)
        overall_start_time = time.time()

        try:
            for i, start_word in enumerate(self.valid_words):
                if i % progress_interval == 0:
                    elapsed = time.time() - overall_start_time
                    logging.info(
                        f"DFS progress: {i}/{total_words} words processed, {elapsed:.2f}s elapsed")

                if time.time() - overall_start_time > 600:  # 10 minute timeout
                    logging.warning("Overall solve timeout reached")
                    break

                solutions = self._dfs(start_word, set(start_word), [start_word],
                                      solution_fingerprints=solution_fingerprints)

                for solution in solutions:
                    solution_set = frozenset(solution)
                    if solution_set not in solution_fingerprints:
                        solution_fingerprints.add(solution_set)
                        unique_solutions.append(solution)

                if len(unique_solutions) >= 1000:  
                    logging.info(
                        f"Found {len(unique_solutions)} total solutions, stopping early")
                    break

        except Exception as e:
            logging.error(f"Error in solve: {str(e)}")

        if len(unique_solutions) == 0:
            logging.warning("No solutions found, try a larger path size")

        return set(unique_solutions)

    def _bfs(self, start_word):
        """Perform BFS starting from the given word with improved resilience"""
        if not start_word or start_word not in self.valid_words:
            logging.warning(f"Invalid start word: {start_word}")
            return []

        if not hasattr(self, 'graph') or not self.graph:
            logging.error("Word graph not initialized")
            return []

        if not isinstance(self.max_path_length, int) or self.max_path_length <= 0:
            logging.warning(
                f"Invalid max_path_length: {self.max_path_length}, using default of 10")
            self.max_path_length = 10

        # Queue entries: (current_word, used_letters, current_chain)
        queue = deque([(start_word, set(start_word), [start_word])])
        all_solutions = []
        visited = set()
        iterations = 0
        fingerprints = set()  # To track unique states
        max_iterations = 1000000  # Safety limit
        max_queue_size = 100000   # Memory safety

        start_time = time.time()
        time_limit = 30  # seconds

        try:
            while queue and iterations < max_iterations:
                iterations += 1

                if iterations % 1000 == 0 and time.time() - start_time > time_limit:
                    logging.warning(
                        f"BFS timed out after {time_limit} seconds for word: {start_word}")
                    break

                if len(queue) > max_queue_size:
                    logging.warning(
                        f"Queue size limit reached ({max_queue_size}) for word: {start_word}")
                    break

                current_word, used_letters, current_chain = queue.popleft()

                state_key = (current_word, frozenset(used_letters))
                if state_key in visited:
                    continue
                visited.add(state_key)

                if len(current_chain) > self.max_path_length:
                    continue

                if self._all_letters_used(used_letters):
                    solution_words = frozenset(current_chain)
                    if solution_words not in fingerprints:
                        fingerprints.add(solution_words)
                        all_solutions.append(tuple(current_chain))
                    continue

                next_words = self.graph.get(current_word, [])
                for next_word in next_words:
                    new_letters = set(next_word) - used_letters
                    if new_letters or not used_letters & set(next_word):
                        new_used_letters = used_letters | set(next_word)
                        new_chain = current_chain + [next_word]
                        queue.append((next_word, new_used_letters, new_chain))

            if iterations >= max_iterations:
                logging.warning(
                    f"BFS reached iteration limit for word: {start_word}")

        except Exception as e:
            logging.error(f"Error in BFS for word {start_word}: {str(e)}")

        return all_solutions

    def solve_bfs(self):
        """Solve using BFS from all possible starting words with improved resilience"""
        if not hasattr(self, 'valid_words') or not self.valid_words:
            logging.error("No valid words available")
            return set()

        all_solutions = set()
        fingerprints = set() 
        total_words = len(self.valid_words)

        progress_interval = max(1, total_words // 10)

        try:
            for i, start_word in enumerate(self.valid_words):
                if i % progress_interval == 0:
                    logging.info(
                        f"BFS progress: {i}/{total_words} words processed")

                solutions = self._bfs(start_word)
                for solution in solutions:
                    solution_set = frozenset(solution)
                    if solution_set not in fingerprints:
                        fingerprints.add(solution_set)
                        all_solutions.update(solutions)

                if len(all_solutions) >= 1000:  
                    logging.info(
                        f"Found {len(all_solutions)} solutions, stopping early")
                    break

        except Exception as e:
            logging.error(f"Error in solve_bfs: {str(e)}")

        if len(all_solutions) == 0:
            logging.warning("No solutions found, try a larger path size")

        return all_solutions


def unique_char_count(word):
    """Count the number of unique chars in the word"""
    return len(set(word))


# %%
class SpellBeeSolver:
    """Solver Class for the NYTimes Spell Bee"""

    def __init__(self, list_of_words, letters):
        self.word_list = list_of_words
        self.letters = letters
        self.center_letter = letters[0]

    def clean_word_list(self):
        """Filter word list to allow for compound words to be used"""
        self.word_list = [
            word.replace("-", "").replace(" ", "").replace("'", "")
            for word in self.word_list
        ]

    def is_valid_word(self, word):
        """Check if the current word is a valid solution"""
        return self.center_letter in word and set(word).issubset(self.letters)

    def is_pangram(self, word):
        """Check if Word is Pangram"""
        return set(word) == set(self.letters)

    def score(self, word):
        """Get the Score For the word based on Spell Bee rules"""
        if len(word) < 4:
            return 0
        if len(word) == 4:
            return 1
        return len(word) + 7 * (self.is_pangram(word))

    def solve(self):
        """Solve the current Letterboxd puzzle"""
        ans = {}
        self.clean_word_list()
        valid_words = list(filter(self.is_valid_word, self.word_list))

        for word in valid_words:
            if self.is_pangram(word):
                print(word)
            ans[word] = self.score(word)
        ans = {word: score for word, score in ans.items() if score > 0}
        ans = dict(sorted(ans.items(), key=lambda item: item[1], reverse=True))
        return ans


def generate_random_box_edges():
    """Generate a set of random input"""
    letters = random.sample(string.ascii_uppercase,
                            12)  
    return [letters[i: i + 3] for i in range(0, 12, 3)]


def test_spell_bee_solver(word_list, todays_word="MAWRING"):
    """Test the solver"""
    letters = list(todays_word)
    spell = SpellBeeSolver(word_list, letters)
    print(spell.solve())


def test_solver(todays_word, word_list):
    # Test the LetterBoxd Solver
    """box_edges = [
        ["M", "R", "E"],  # Top edge
        ["U", "F", "H"],  # Right edge
        ["G", "S", "T"],  # Bottom edge
        ["L", "A", "Y"],  # Left edge
    ]"""
    # Each box edge is a represented by continuous chars, so E1 is CURR_WORD[0:3] and so on

    box_edges = [list(todays_word[i: i + 3])
                 for i in range(0, len(todays_word), 3)]

    graph_solver = GraphLetterBoxedSolver(
        word_list, box_edges, max_path_length=3)

    solutions = graph_solver.solve_bfs()

    print(f"{len(solutions)} solutions found:")
    for solution in solutions:
        print(solution)


# %%
def generate_random_test_cases(max_iters, word_list):
    """Generate Some Test Cases to Check Behaviour"""
    iterations = 0
    while True:
        iterations += 1
        box_edges = generate_random_box_edges()

        solver = GraphLetterBoxedSolver(
            word_list, box_edges, max_path_length=1)
        solutions = solver.solve()
        if solutions or iterations > max_iters:
            print("Solution found after", iterations, "iterations")
            print("Box edges:", box_edges)
            print("Solution:", solutions)
            break


if __name__ == "__main__":
    word_list = read_word_list(
        "/Users/dhruvcharan/Desktop/dsa/12dicts-6.0.2/American/2of12.txt"
    )
    test_solver("ORACTLJSXNIU", word_list)
    test_spell_bee_solver(word_list, "OZTANIC")

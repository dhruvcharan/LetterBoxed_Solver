# %%
import random
import string
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx


def read_word_list(filename):
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
        self.valid_words = filter_valid_words(self.cleaned_word_list, box_edges)
        random.shuffle(self.valid_words)
        self.graph = self._build_graph(self.valid_words)
        self.letters = set(letter for word in self.valid_words for letter in word)
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
        G = nx.DiGraph()  # Create a directed graph
        for word, connections in self.graph.items():
            for connected_word in connections:
                G.add_edge(word, connected_word)

        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)
        nx.draw(
            G,
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

    def _dfs(self, current_word, used_letters, current_chain):

        if len(current_chain) > self.max_path_length:
            return []

        if self._all_letters_used(used_letters):
            return [tuple(current_chain)]

        all_solutions = []
        for next_word in self.graph[current_word]:
            new_letters = (
                set(next_word) - used_letters
            )  # Letters that are new and haven't been used
            if new_letters or not used_letters & set(
                next_word
            ):  # Allow overlap if it contributes new letters
                new_used_letters = used_letters | set(next_word)
                result = self._dfs(
                    next_word, new_used_letters, current_chain + [next_word]
                )
                if result:
                    all_solutions.extend(result)

        return all_solutions

    def solve(self):
        all_solutions = set()
        # Try every word as the starting point
        for start_word in self.valid_words:
            solutions = self._dfs(start_word, set(start_word), [start_word])
            all_solutions.update(solutions)
        if len(all_solutions) == 0:
            print("No solutions found, try a larger path size")
        return all_solutions

    # The box edges are represented as a list of lists of chars


def unique_char_count(word):
    return len(set(word))


# %%
class SpellBeeSolver:
    def __init__(self, list_of_words, letters):
        self.word_list = list_of_words
        self.letters = letters
        self.center_letter = letters[0]

    def clean_word_list(self):
        self.word_list = [
            word.replace("-", "").replace(" ", "").replace("'", "")
            for word in self.word_list
        ]

    def is_valid_word(self, word):
        return self.center_letter in word and set(word).issubset(self.letters)

    def is_pangram(self, word):
        return set(word) == set(self.letters)

    def score(self, word):
        if len(word) < 4:
            return 0
        if len(word) == 4:
            return 1
        return len(word) + 7 * (self.is_pangram(word))

    def solve(self):
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
    letters = random.sample(string.ascii_uppercase, 12)  # Select 12 unique letters
    return [letters[i : i + 3] for i in range(0, 12, 3)]


def test_spell_bee_solver(todays_word="MAWRING"):
    letters = list(todays_word)
    spell = SpellBeeSolver(word_list, letters)
    print(spell.solve())


def test_solver(todays_word="TIAUWLDBYRMO"):
    # Test the LetterBoxd Solver
    """box_edges = [
        ["M", "R", "E"],  # Top edge
        ["U", "F", "H"],  # Right edge
        ["G", "S", "T"],  # Bottom edge
        ["L", "A", "Y"],  # Left edge
    ]"""
    # Each box edge is a represented by continuous chars, so E1 is CURR_WORD[0:3] and so on

    box_edges = [list(todays_word[i : i + 3]) for i in range(0, len(todays_word), 3)]

    # box_edges = generate_random_box_edges()
    graph_solver = GraphLetterBoxedSolver(word_list, box_edges)

    solutions = graph_solver.solve()

    print(f"{len(solutions)} solutions found:")
    for solution in solutions:
        print(solution)


# %%
def generate_random_test_cases(max_iters,word_list):
    iterations = 0
    while True:
        iterations += 1
        box_edges = generate_random_box_edges()

        solver = GraphLetterBoxedSolver(word_list, box_edges, max_path_length=1)
        solutions = solver.solve()
        if solutions or iterations > max_iters:
            print("Solution found after", iterations, "iterations")
            print("Box edges:", box_edges)
            print("Solution:", solutions)
            break


    
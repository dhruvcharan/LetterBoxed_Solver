import pytest
from collections import defaultdict
import os
from typing import List, Set, Dict, Tuple

# filepath: /Users/dhruvcharan/code/Letterboxdsolver-django/test_letterboxd_solver.py

# Import classes and functions from the module
from letterboxd_solver import (
    read_word_list,
    is_valid_word,
    filter_valid_words,
    GraphLetterBoxedSolver
)

# Test fixtures
@pytest.fixture
def simple_box_edges():
    return [
        ["A", "B", "C"],
        ["D", "E", "F"],
        ["G", "H", "I"],
        ["J", "K", "L"]
    ]

@pytest.fixture
def small_box_edges():
    return [
        ["A", "B"],
        ["C", "D"],
        ["E", "F"],
        ["G", "H"]
    ]

@pytest.fixture
def simple_word_list():
    return ["ABC", "CAT", "BAT", "DOG", "CLAW", "LAMB", "BIKE", "EGG", "FIG", "HAT", "JOB"]

@pytest.fixture
def connectivity_word_list():
    return ["ADE", "EFG", "GHB", "BCA", "AJK", "KLH"]

@pytest.fixture
def simple_solver(simple_word_list, simple_box_edges):
    return GraphLetterBoxedSolver(simple_word_list, simple_box_edges, max_path_length=2)

@pytest.fixture
def connectivity_solver(connectivity_word_list, small_box_edges):
    return GraphLetterBoxedSolver(connectivity_word_list, small_box_edges, max_path_length=3)

# Test helper functions
def test_read_word_list(tmp_path):
    # Create a temporary word list file
    word_file = tmp_path / "test_words.txt"
    word_file.write_text("apple\nbanana\ncherry\n")
    
    words = read_word_list(str(word_file))
    assert words == ["APPLE", "BANANA", "CHERRY"]

def test_is_valid_word():
    box_edges = [["A", "B", "C"], ["D", "E", "F"]]
    
    # Valid words - letters from different edges
    assert is_valid_word("ABDEF", box_edges) == True
    assert is_valid_word("FACE", box_edges) == True
    assert is_valid_word("BFDAC", box_edges) == True
    
    # Invalid: consecutive letters from same edge
    assert is_valid_word("ABCDE", box_edges) == False
    assert is_valid_word("DEFAB", box_edges) == False
    
    # Invalid: letter not in any edge
    assert is_valid_word("ABCX", box_edges) == False
    assert is_valid_word("ZABDEF", box_edges) == False
    
    # Edge cases
    assert is_valid_word("", box_edges) == True  # Empty word is technically valid
    assert is_valid_word("A", box_edges) == True  # Single letter is valid

def test_filter_valid_words():
    box_edges = [["A", "B", "C"], ["D", "E", "F"]]
    words = ["ABDEF", "FACE", "ABCDE", "ABCX", "BAD", "FAB"]
    
    filtered = filter_valid_words(words, box_edges)
    assert set(filtered) == {"ABDEF", "FACE", "BAD", "FAB"}
    
    # Test with empty word list
    assert filter_valid_words([], box_edges) == []
    
    # Test with no valid words
    assert filter_valid_words(["ABCC", "XXYZ"], box_edges) == []

# Test GraphLetterBoxedSolver class methods
def test_init(simple_solver, simple_box_edges):
    # Test that the solver initialized correctly
    assert simple_solver.max_path_length == 2
    
    # Test that valid_words contains only words that follow the rules
    for word in simple_solver.valid_words:
        assert is_valid_word(word, simple_box_edges)
    
    # Test that the graph was built
    assert isinstance(simple_solver.graph, defaultdict)
    
    # Test that the letters set is populated
    assert isinstance(simple_solver.letters, set)
    assert len(simple_solver.letters) > 0

def test_init_with_special_chars():
    # Test initialization with words containing special characters
    box_edges = [["A", "B", "C"], ["D", "E", "F"]]
    words = ["A-BC", "C'AT", "B AT"]
    
    solver = GraphLetterBoxedSolver(words, box_edges)
    
    # Check that special chars were removed
    assert "ABC" in solver.cleaned_word_list
    assert "CAT" in solver.cleaned_word_list
    assert "BAT" in solver.cleaned_word_list

def test_build_graph(simple_word_list, simple_box_edges):
    solver = GraphLetterBoxedSolver(simple_word_list, simple_box_edges)
    graph = solver.graph
    
    # Test graph structure
    for word1 in solver.valid_words:
        for word2 in solver.valid_words:
            if word1 != word2 and word1[-1] == word2[0]:
                assert word2 in graph[word1], f"{word2} should be connected to {word1}"
            elif word1 != word2 and word1[-1] != word2[0]:
                assert word2 not in graph[word1], f"{word2} should not be connected to {word1}"

def test_all_letters_used(simple_solver):
    # Test with all letters
    all_letters = simple_solver.letters
    assert simple_solver._all_letters_used(all_letters) == True
    
    # Test with subset of letters
    subset = set(list(all_letters)[0:len(all_letters)//2])
    assert simple_solver._all_letters_used(subset) == False
    
    # Test with empty set
    assert simple_solver._all_letters_used(set()) == False
    
    # Test with just one missing letter
    almost_all = set(all_letters)
    if almost_all:
        almost_all.pop()
        assert simple_solver._all_letters_used(almost_all) == False

def test_dfs_basic(monkeypatch):
    """Test the _dfs method with a simple controlled example"""
    # Create a simple test graph where we know what the result should be
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    words = ["ACD", "DEF", "FGA", "ABH"]
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=3)
    
    # Create a test environment where we know the graph structure
    test_graph = defaultdict(list)
    test_graph["ACD"] = ["DEF"]
    test_graph["DEF"] = ["FGA"]
    test_graph["FGA"] = ["ABH"]
    test_graph["ABH"] = ["ACD"]
    
    # Override the solver's graph with our test graph
    monkeypatch.setattr(solver, "graph", test_graph)
    monkeypatch.setattr(solver, "letters", set("ABCDEFGH"))
    
    # Start DFS from "ACD"
    results = solver._dfs("ACD", set("ACD"), ["ACD"], set())
    
    # We expect to find a solution that covers all letters
    expected_path = ("ACD", "DEF", "FGA")
    assert any(path[:3] == expected_path for path in results)

def test_dfs_max_depth(monkeypatch):
    """Test that _dfs respects max_path_length"""
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    words = ["ACD", "DEF", "FGA", "ABH"]
    
    # With max_path_length=2
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=2)
    
    test_graph = defaultdict(list)
    test_graph["ACD"] = ["DEF"]
    test_graph["DEF"] = ["FGA"]
    test_graph["FGA"] = ["ABH"]
    test_graph["ABH"] = ["ACD"]
    
    monkeypatch.setattr(solver, "graph", test_graph)
    monkeypatch.setattr(solver, "letters", set("ABCDEFGH"))
    
    # DFS should not go deeper than max_path_length
    results = solver._dfs("ACD", set("ACD"), ["ACD"], set())
    
    # No solution should exist with just 2 words
    assert len(results) == 0

def test_dfs_pruning(monkeypatch):
    """Test that _dfs correctly prunes paths already explored"""
    box_edges = [["A", "B"], ["C", "D"]]
    words = ["AC", "CB", "BD", "DA"]
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=4)
    
    test_graph = defaultdict(list)
    test_graph["AC"] = ["CB"]
    test_graph["CB"] = ["BD"]
    test_graph["BD"] = ["DA"]
    test_graph["DA"] = ["AC"]
    
    monkeypatch.setattr(solver, "graph", test_graph)
    monkeypatch.setattr(solver, "letters", set("ABCD"))
    
    # Using a test memo to see if pruning works
    memo = {("AC", "CB"): [("AC", "CB", "BD")]}
    
    results = solver._dfs("AC", set("AC"), ["AC"], memo)
    
    # Should use the memoized result instead of recomputing
    assert ("AC", "CB", "BD") in results

def test_solve():
    """Test the solve method with a complete example"""
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    # Create words that can form a valid solution
    words = ["ACD", "DEF", "FGB", "BAH", "HCE"]
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=3)
    solutions = solver.solve()
    
    # Check that we found at least one solution
    assert len(solutions) > 0
    
    # Verify solutions are valid
    for solution in solutions:
        # Check that solution length is within max_path_length
        assert len(solution) <= solver.max_path_length
        
        # Check that each transition is valid
        for i in range(len(solution) - 1):
            assert solution[i][-1] == solution[i+1][0]
        
        # Check that all letters are used
        used_letters = set()
        for word in solution:
            used_letters.update(set(word))
        assert used_letters == solver.letters

def test_solve_bfs():
    """Test the solve_bfs method"""
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    words = ["ACD", "DEF", "FGB", "BAH", "HCE"]
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=3)
    solutions = solver.solve_bfs()
    
    # Check that we found solutions
    assert len(solutions) > 0
    
    # Verify solutions are valid
    for solution in solutions:
        # Check solution length
        assert len(solution) <= solver.max_path_length
        
        # Check transitions
        for i in range(len(solution) - 1):
            assert solution[i][-1] == solution[i+1][0]
        
        # Check letter coverage
        used_letters = set()
        for word in solution:
            used_letters.update(set(word))
        assert used_letters == solver.letters

def test_bfs_method():
    """Test the _bfs method"""
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    words = ["ACD", "DEF", "FGB", "BAH", "HCE"]
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=3)
    
    # Test BFS from a specific starting word
    results = solver._bfs("ACD")
    
    # Verify results
    assert len(results) > 0
    
    # First result should be the shortest valid path
    first_solution = results[0]
    assert len(first_solution) <= solver.max_path_length
    
    # Check that solution covers all letters
    used_letters = set()
    for word in first_solution:
        used_letters.update(set(word))
    assert used_letters == solver.letters

def test_empty_word_list():
    """Test behavior with empty word list"""
    box_edges = [["A", "B"], ["C", "D"]]
    solver = GraphLetterBoxedSolver([], box_edges)
    
    # No valid words
    assert len(solver.valid_words) == 0
    
    # Graph should be empty
    assert len(solver.graph) == 0
    
    # No solutions
    assert len(solver.solve()) == 0
    assert len(solver.solve_bfs()) == 0

def test_no_solution_case():
    """Test when no solution exists"""
    box_edges = [["A", "B"], ["C", "D"], ["E", "F"], ["G", "H"]]
    # Words that can't form a solution that covers all letters
    words = ["ACD", "CDA", "ACE"]  # Only covers A, C, D, E
    
    solver = GraphLetterBoxedSolver(words, box_edges, max_path_length=3)
    
    # No solutions should be found
    assert len(solver.solve()) == 0
    assert len(solver.solve_bfs()) == 0

# Daily NYTimes Letterboxd and SpellBee Solver

This repository contains a Python-based solver for the daily NYTimes Letterboxd and SpellBee puzzles.

I plan on converting this into a Django Based WebApp that fetches the current puzzles and shows a more interactive UI but the current implementation is the barebones CLI based demo


## Getting Started

### Prerequisites

- Python (version specified in `.python-version`)
- Required Python packages (specified in `pyproject.toml`)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/LetterBoxed_Solver.git
    cd Letterboxd_Solver
    ```

2. Install the required packages using `uv`:

    ```sh
    uv sync
    ```

    - This will install all dependencies specified in the [pyproject.toml] file and manage the dependency graph.

3. Verify the installation:

    ```sh
    uv doctor
    ```

    - This command checks for any issues with the dependency graph or environment setup.

---

### Usage

Run [main.py] using `uv` to ensure the correct virtual environment is activated:

```sh
uv run python main.py
```

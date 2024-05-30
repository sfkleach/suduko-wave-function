from typing import TypeAlias, Generator

Grid: TypeAlias = list[list[int]]
SetGrid: TypeAlias = list[list[set[int]]]

# Examples from https://sudoku.com/
EXAMPLE = """
___83_6__
1____5___
5_3__2497
__9__83__
3___1_7_6
_126_____
9___2_87_
___749__2
62_3__954
"""

HARD = """
_____2___
___6_3___
_9_7____2
__2_14__8
37_82___1
185_6____
53____9__
__9___257
82_94____
"""

EXPERT = """
46_98_3__
__97_6_2_
_____19__
5_61_4___
_42___6__
____6547_
9________
657329___
2______93
"""

EXTREME = """
_5_____2_
__64__13_
4___9____
___1____2
__8_____9
_3__7_81_
__39__64_
________8
_7___5___
"""

def convert_to_grid(s: str) -> list[list[int]]:
    return [
        [int(c) if c != '_' else 0 for c in line]
        for line in s.splitlines()
        if line
    ]

SUDOKU = convert_to_grid(EXTREME)

EXPECTED = """
+---+---+---+---+---+---+---+---+---+
| 2 │ 9 │ 4 | 8 │ 3 │ 7 | 6 │ 1 │ 5 |
+---+---+---+---+---+---+---+---+---+
| 1 │ 7 │ 6 | 4 │ 9 │ 5 | 2 │ 3 │ 8 |
+---+---+---+---+---+---+---+---+---+
| 5 │ 8 │ 3 | 1 │ 6 │ 2 | 4 │ 9 │ 7 |
+---+---+---+---+---+---+---+---+---+
| 7 │ 6 │ 9 | 2 │ 5 │ 8 | 3 │ 4 │ 1 |
+---+---+---+---+---+---+---+---+---+
| 3 │ 5 │ 8 | 9 │ 1 │ 4 | 7 │ 2 │ 6 |
+---+---+---+---+---+---+---+---+---+
| 4 │ 1 │ 2 | 6 │ 7 │ 3 | 5 │ 8 │ 9 |
+---+---+---+---+---+---+---+---+---+
| 9 │ 4 │ 1 | 5 │ 2 │ 6 | 8 │ 7 │ 3 |
+---+---+---+---+---+---+---+---+---+
| 8 │ 3 │ 5 | 7 │ 4 │ 9 | 1 │ 6 │ 2 |
+---+---+---+---+---+---+---+---+---+
| 6 │ 2 │ 7 | 3 │ 8 │ 1 | 9 │ 5 │ 4 |
+---+---+---+---+---+---+---+---+---+"""

def new_sudoku(grid: Grid) -> SetGrid:
    return [
        [
            {n} if n else set(range(1,10))
            for n in row
        ]
        for row in grid
    ]

def pretty(grid: SetGrid):
    # print(grid)
    # return

    def cellstr(x):
        if len(x) > 5:
            return x[0:4]+"+"
        else:
            n2 = ( 5 - len(x) ) // 2
            n1 = 5 - len(x) - n2
            return " " * n1 + x + " " * n2

    print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")
    sep = None
    for row in grid:
        if sep is not None:
            print(sep)
        print("|", end="")
        for cell in row:
            txt = "".join(map(str, cell))
            print(f"{cellstr(txt)}", end="|")
        print()
        sep = "+-----+-----+-----+-----+-----+-----+-----+-----+-----+"
    print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")


def find_minimum_set(grid: SetGrid) -> tuple[int, int] | None:
    sofar = 9
    (i, j) = (-1, -1)
    for r, row in enumerate(grid):
        for c, col in enumerate(row):
            L = len(col)  # Size of set.
            if 2 <= L < sofar:
                sofar = L
                i, j = r, c
    if i == -1:
        return None
    else:
        return (i, j)


def find_box_values(grid: Grid, row: int, col: int) -> set[int]:
    """Find the values in the 3x3 containing box"""
    box_row = row // 3 * 3
    box_col = col // 3 * 3
    elements = {
        grid[row][col]
        for row in range(box_row, box_row + 3)
        for col in range(box_col, box_col + 3)
    }
    return elements


def find_singleton_box_set_values(grid: SetGrid, irow: int, icol: int) -> set[int]:
    """Find the values in the 3x3 containing box"""
    box_row = irow // 3 * 3
    box_col = icol // 3 * 3
    values = set()
    for row in range(box_row, box_row + 3):
        for col in range(box_col, box_col + 3):
            if row != irow and col != icol:
                if len(grid[row][col]) == 1:
                    values |= grid[row][col]
    return values


def calculate_initial_options(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col] != 0:
        return {grid[row][col]}
    row_values = set(grid[row]) - {grid[row][col]}
    col_values = {grid[r][col] for r in range(9)} - {grid[row][col]}
    box_values = find_box_values(grid, row, col) - {grid[row][col]}
    options = set(range(1, 10)) - row_values - col_values - box_values
    return options


def calculate_options(grid: SetGrid, row: int, col: int) -> set[int]:

    def other_row_values() -> Generator[set[int], None, None]:
        """Find the values in the row that are already taken, excluding the current cell"""
        for c, value_set in enumerate(grid[row]):
            if c != col:
                yield value_set

    def other_col_values() -> Generator[set[int], None, None]:
        """Find the values in the column that are already taken, excluding the current cell"""
        for r in range(9):
            if r != row:
                yield grid[r][col]

    def taken_row_values():
        """Find the values in the row that are already taken, excluding the current cell"""
        for value_set in other_row_values():
            if len(value_set) == 1:
                yield next(iter(value_set)))

    def taken_col_values():
        """Find the values in the column that are already taken, excluding the current cell"""
        for value_set in other_col_values():
            if len(value_set) == 1:
                yield next(iter(value_set))

    def forced_row_value():
        """Find the value that is forced by the other values in the row"""
        other_values = set()
        for c, value_set in enumerate(grid[row]):
            if len(value_set) == 1 and c != col:
                other_values |= value_set
        

    singleton_row_values = set(taken_row_values())
    singleton_col_values = set(taken_col_values())
    box_values = find_singleton_box_set_values(grid, row, col)
    # print(f"{grid[row][col]},srv={singleton_row_values}, src={singleton_col_values}, bv={box_values}")
    options = grid[row][col] - singleton_row_values - singleton_col_values - box_values
    return options

def propagate_constraints(grid: SetGrid) -> SetGrid:
    return [[calculate_options(grid, row, col) for col in range(9)] for row in range(9)]

"""
THE PLAN:
1. First convert the sudoku to a set sudoku of all possible options
2. Collapse all singletons
3. Find the smallest non singleton-set
4. Pick one of its values and just set it (w backtracking)
5. Calculate new setgrid 
6. go again
"""

def is_valid(grid: SetGrid) -> bool:
    for row in grid:
        for cell in row:
            if not cell:
                return False
    return True

def simplify(grid: SetGrid) -> Generator[SetGrid, None, None]:
    while is_valid(grid):
        g = propagate_constraints(grid)
        if g == grid:
            yield grid
            break
        grid = g

def solve(grid: SetGrid, guesses) -> Generator[SetGrid, None, None]:
    pretty(grid)
    print()
    for sg in simplify(grid):
        if minimum := find_minimum_set(sg):
            row, col = minimum
            L = list(sg[row][col])
            for choice in L:
                new_guesses = [ f"Guessing {row=}, {col=}, {choice=}", *guesses ]       
                print(f"Guesses: {new_guesses}")
                sg[row][col] = {choice}
                yield from solve(sg, new_guesses)
        else:
            print( 'SOLUTION' )
            yield sg
    
GS = solve(next(simplify(new_sudoku(SUDOKU))), [])
G = next(GS)

pretty(G)


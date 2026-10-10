"""Sudoku with CP-SAT, and a check that the solution is unique."""
from ortools.sat.python import cp_model

puzzle = """
.9...4...
...5.7.32
..123....
.......2.
7...261.4
.6..8...7
1.4...89.
.8....273
.........
""".split()

m = cp_model.CpModel()
x = [[m.new_int_var(1, 9, f"x{r}{c}") for c in range(9)] for r in range(9)]
for i in range(9):
    m.add_all_different(x[i])                            # row i
    m.add_all_different(x[r][i] for r in range(9))       # column i
for br in range(0, 9, 3):
    for bc in range(0, 9, 3):                            # 3 x 3 boxes
        m.add_all_different(x[br + i][bc + j]
                            for i in range(3) for j in range(3))
for r in range(9):
    for c in range(9):
        if puzzle[r][c] != ".":
            m.add(x[r][c] == int(puzzle[r][c]))


class Counter(cp_model.CpSolverSolutionCallback):
    """Called by the solver for every solution it finds."""
    def __init__(self, variables):
        super().__init__()
        self.variables, self.count = variables, 0

    def on_solution_callback(self):
        self.count += 1
        if self.count == 1:
            for row in self.variables:
                print(" ".join(str(self.value(v)) for v in row))


solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True     # do not stop at one
counter = Counter(x)
solver.solve(m, counter)
print(f"Number of solutions: {counter.count}")

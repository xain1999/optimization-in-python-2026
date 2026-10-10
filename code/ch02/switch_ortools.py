"""Create OR-Tools linear solvers by name and solve the same model."""
from ortools.linear_solver import pywraplp

for name in ["GLOP", "PDLP", "SCIP", "CBC"]:
    solver = pywraplp.Solver.CreateSolver(name)
    if solver is None:
        print(f"{name:<6} not available in this build")
        continue
    desks = solver.NumVar(0, solver.infinity(), "desks")
    shelves = solver.NumVar(0, solver.infinity(), "shelves")
    solver.Add(4 * desks + 3 * shelves <= 240)
    solver.Add(2 * desks + shelves <= 100)
    solver.Add(shelves <= 60)
    solver.Maximize(70 * desks + 50 * shelves)
    solver.Solve()
    print(f"{name:<6} profit = {solver.Objective().Value():,.2f}")

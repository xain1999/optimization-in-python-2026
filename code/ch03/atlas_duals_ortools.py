from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")
desks = solver.NumVar(0, solver.infinity(), "desks")
shelves = solver.NumVar(0, solver.infinity(), "shelves")
carpentry = solver.Add(4 * desks + 3 * shelves <= 240, "Carpentry")
finishing = solver.Add(2 * desks + shelves <= 100, "Finishing")
demand = solver.Add(shelves <= 60, "Shelf_demand")
solver.Maximize(70 * desks + 50 * shelves)
solver.Solve()

for c in [carpentry, finishing, demand]:
    print(f"{c.name():<14} dual = {c.dual_value() + 0.0:6.2f}")
for v in [desks, shelves]:
    print(f"{v.name():<14} reduced cost = {v.reduced_cost() + 0.0:6.2f}")

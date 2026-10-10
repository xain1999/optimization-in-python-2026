from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

desks   = solver.NumVar(0, solver.infinity(), "desks")
shelves = solver.NumVar(0, solver.infinity(), "shelves")

solver.Add(4 * desks + 3 * shelves <= 240)   # carpentry
solver.Add(2 * desks + 1 * shelves <= 100)   # finishing
solver.Add(shelves <= 60)                    # shelf demand

solver.Maximize(70 * desks + 50 * shelves)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Desks:   {desks.solution_value():.1f}")
    print(f"Shelves: {shelves.solution_value():.1f}")
    print(f"Profit:  {solver.Objective().Value():,.0f}")

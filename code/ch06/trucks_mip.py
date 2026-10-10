"""Truck loading as a MILP with OR-Tools' linear solver interface (SCIP)."""
from ortools.linear_solver import pywraplp
from pallet_data import pallets, trucks, max_pallets

solver = pywraplp.Solver.CreateSolver("SCIP")

# x[p, t] = 1 if pallet p goes on truck t
x = {(p, t): solver.BoolVar(f"x_{p}_{t}") for p in pallets for t in trucks}
# food[t] = 1 if truck t carries any food (then it may not carry chemicals)
food = {t: solver.BoolVar(f"food_{t}") for t in trucks}

for p in pallets:                                 # each pallet at most once
    solver.Add(sum(x[p, t] for t in trucks) <= 1)

for t, cap in trucks.items():
    solver.Add(sum(pallets[p][0] * x[p, t] for p in pallets) <= cap)
    solver.Add(sum(x[p, t] for p in pallets) <= max_pallets)
    for p, (_, _, kind) in pallets.items():
        if kind == "food":                        # food on t => food[t] = 1
            solver.Add(x[p, t] <= food[t])
        elif kind == "chemical":                  # chemical on t => no food
            solver.Add(x[p, t] <= 1 - food[t])

solver.Maximize(sum(pallets[p][1] * x[p, t] for p in pallets for t in trucks))
solver.SetTimeLimit(30_000)                       # milliseconds
status = solver.Solve()

names = {solver.OPTIMAL: "OPTIMAL", solver.FEASIBLE: "FEASIBLE"}
print("Status:", names.get(status, status))
for t in trucks:
    load = [p for p in pallets if x[p, t].solution_value() > 0.5]
    kg = sum(pallets[p][0] for p in load)
    print(f"  {t}: {' '.join(load):<16} {kg:>5} kg")
print(f"Value shipped: ${solver.Objective().Value():,.0f}")
print(f"Solve time: {solver.wall_time() / 1000:.2f} s, nodes: {solver.nodes()}")

"""Sahara Snacks (Chapter 5) with OR-Tools' linear solver interface."""
import sys
sys.path.append("../ch05")
from snacks_model import load_data
from ortools.linear_solver import pywraplp

d = load_data("../ch05/data")
solver = pywraplp.Solver.CreateSolver("GLOP")
inf = solver.infinity()

make = {(p, k): solver.NumVar(0, inf, f"make_{p}_{k}") for p, k in d["arcs"]}

# Ranged constraints: one row  L <= sum <= U  per product.
demand = {}
for p in d["P"]:
    demand[p] = solver.Constraint(d["min_dem"][p], d["max_dem"][p], f"dem_{p}")
    for pp, k in d["arcs"]:
        if pp == p:
            demand[p].SetCoefficient(make[pp, k], 1)

hours = {k: solver.Add(sum(d["hours"][p, kk] * make[p, kk]
                           for p, kk in d["arcs"] if kk == k)
                       <= d["hours_avail"][k], f"hours_{k}")
         for k in d["K"]}

solver.Maximize(sum((d["price"][p] - d["cost"][p, k]) * make[p, k]
                    for p, k in d["arcs"]))
status = solver.Solve()
assert status == pywraplp.Solver.OPTIMAL

print(f"Profit: {solver.Objective().Value():,.0f}")
print("Shadow prices of plant hours:",
      {k: round(c.dual_value(), 2) for k, c in hours.items()})
print("Demand rows at a bound:",
      {p: round(c.dual_value(), 2) for p, c in demand.items()
       if abs(c.dual_value()) > 1e-9})
print(f"Constraints: {solver.NumConstraints()}, "
      f"variables: {solver.NumVariables()}")

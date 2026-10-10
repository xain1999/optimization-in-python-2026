"""Solve the same PuLP model with three different solvers."""
import pulp

def build_model():
    model = pulp.LpProblem("Atlas_Furniture", pulp.LpMaximize)
    desks = model.add_variable("desks", lowBound=0)
    shelves = model.add_variable("shelves", lowBound=0)
    model += 70 * desks + 50 * shelves
    model += 4 * desks + 3 * shelves <= 240, "Carpentry"
    model += 2 * desks + 1 * shelves <= 100, "Finishing"
    model += shelves <= 60, "Shelf_demand"
    return model

solvers = {
    "HiGHS": pulp.HiGHS(msg=False),
    "CBC":   pulp.COIN_CMD(msg=False),
    "GLPK":  pulp.PYGLPK(msg=False),
}

for name, solver in solvers.items():
    if not solver.available():
        print(f"{name:<6} not installed - skipped")
        continue
    model = build_model()
    result = model.solve(solver)
    print(f"{name:<6} {result.status_str:<8} "
          f"profit = {pulp.value(model.objective):,.0f}  "
          f"time = {result.time:.3f}s")

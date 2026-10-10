"""Confirm a shadow price by re-solving with more of a resource."""
import pulp

def solve_atlas(carpentry_hours):
    model = pulp.LpProblem("Atlas_Furniture", pulp.LpMaximize)
    desks = model.add_variable("desks", lowBound=0)
    shelves = model.add_variable("shelves", lowBound=0)
    model += 70 * desks + 50 * shelves
    model += 4 * desks + 3 * shelves <= carpentry_hours, "Carpentry"
    model += 2 * desks + 1 * shelves <= 100, "Finishing"
    model += shelves <= 60, "Shelf_demand"
    model.solve(pulp.HiGHS(msg=False))
    return pulp.value(model.objective)

base = solve_atlas(240)
for hours in [241, 250, 260, 270, 300]:
    gain = solve_atlas(hours) - base
    print(f"{hours} hours: profit {base + gain:7,.0f}  "
          f"gain {gain:5.0f}  per extra hour {gain / (hours - 240):5.2f}")

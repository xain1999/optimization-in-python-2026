"""Shadow prices, slacks and reduced costs for the Atlas model in PuLP."""
import pulp

model = pulp.LpProblem("Atlas_Furniture", pulp.LpMaximize)
desks = model.add_variable("desks", lowBound=0)
shelves = model.add_variable("shelves", lowBound=0)
model += 70 * desks + 50 * shelves
model += 4 * desks + 3 * shelves <= 240, "Carpentry"
model += 2 * desks + 1 * shelves <= 100, "Finishing"
model += shelves <= 60, "Shelf_demand"
model.solve(pulp.HiGHS(msg=False))

print(f"{'Constraint':<14}{'slack':>8}{'dual (pi)':>12}")
for c in model.constraints():
    print(f"{c.name:<14}{c.slack + 0.0:8.1f}{c.pi + 0.0:12.2f}")
print(f"{'Variable':<14}{'value':>8}{'reduced cost':>14}")
for v in model.variables():
    print(f"{v.name:<14}{v.value():8.1f}{v.dj + 0.0:14.2f}")

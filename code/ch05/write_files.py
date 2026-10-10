"""Write a model to LP, MPS and JSON files, and read it back."""
import pulp

model = pulp.LpProblem("Atlas_Furniture", pulp.LpMaximize)
desks = model.add_variable("desks", lowBound=0, cat="Integer")
shelves = model.add_variable("shelves", lowBound=0, upBound=60)
model += 70 * desks + 50 * shelves, "Profit"
model += 4 * desks + 3 * shelves <= 240, "Carpentry"
model += 2 * desks + 1 * shelves <= 100, "Finishing"

model.writeLP("atlas.lp")          # human-readable
model.writeMPS("atlas.mps")        # standard exchange format
model.to_json("atlas.json")        # PuLP's own format, keeps everything

variables, copy = pulp.LpProblem.from_json("atlas.json")
copy.solve(pulp.HiGHS(msg=False))
print("Re-loaded model:", {n: v.value() for n, v in variables.items()},
      "profit =", pulp.value(copy.objective))

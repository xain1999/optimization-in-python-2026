"""Choosing expansion projects with logical constraints."""
import pulp

projects = {   # name: (net present value $k, investment $k)
    "new_saw":       (180, 120),
    "spray_booth":   (150, 100),
    "cnc_router":    (260, 210),
    "second_shift":  (120,  40),
    "warehouse":     (140, 150),
    "online_shop":   ( 90,  60),
}
budget = 400
P = list(projects)

model = pulp.LpProblem("Project_Selection", pulp.LpMaximize)
y = model.add_variable_dict("select", P, cat="Binary")

model += pulp.lpSum(projects[p][0] * y[p] for p in P), "NPV"
model += pulp.lpSum(projects[p][1] * y[p] for p in P) <= budget, "Budget"

# 1. The CNC router replaces the saw: choose at most one of them.
model += y["new_saw"] + y["cnc_router"] <= 1, "Exclusive"
# 2. The online shop needs the warehouse (if shop, then warehouse).
model += y["online_shop"] <= y["warehouse"], "Shop_needs_warehouse"
# 3. Management will supervise at most three new projects.
model += pulp.lpSum(y[p] for p in P) <= 3, "Max_three"
# 4. At least one capacity project: saw, router or second shift.
model += (y["new_saw"] + y["cnc_router"] + y["second_shift"] >= 1,
          "Capacity_project")

result = model.solve(pulp.HiGHS(msg=False))
chosen = [p for p in P if y[p].value() > 0.5]
print("Selected:", ", ".join(chosen))
print(f"NPV = ${pulp.value(model.objective):,.0f}k,  "
      f"investment = ${sum(projects[p][1] for p in chosen):,}k")

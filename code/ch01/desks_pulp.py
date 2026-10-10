import pulp

model = pulp.LpProblem("Atlas_Furniture", pulp.LpMaximize)

desks   = model.add_variable("desks", lowBound=0)
shelves = model.add_variable("shelves", lowBound=0)

model += 70 * desks + 50 * shelves, "Profit"
model += 4 * desks + 3 * shelves <= 240, "Carpentry"
model += 2 * desks + 1 * shelves <= 100, "Finishing"
model += shelves <= 60, "Shelf_demand"

result = model.solve(pulp.HiGHS(msg=False))

print("Status: ", result.status_str)
print(f"Desks:   {desks.value():.1f}")
print(f"Shelves: {shelves.value():.1f}")
print(f"Profit:  {pulp.value(model.objective):,.0f}")

import pulp

# ---- Data -------------------------------------------------------
products  = ["desk", "shelf", "table", "chair"]
resources = ["carpentry", "finishing", "wood"]

profit = {"desk": 70, "shelf": 50, "table": 90, "chair": 24}

usage = {  # hours (or board-metres) per unit
    ("carpentry", "desk"): 4, ("carpentry", "shelf"): 3,
    ("carpentry", "table"): 6, ("carpentry", "chair"): 1,
    ("finishing", "desk"): 2, ("finishing", "shelf"): 1,
    ("finishing", "table"): 3, ("finishing", "chair"): 1,
    ("wood", "desk"): 5, ("wood", "shelf"): 4,
    ("wood", "table"): 8, ("wood", "chair"): 2,
}
capacity = {"carpentry": 400, "finishing": 180, "wood": 520}
max_demand = {"desk": 50, "shelf": 60, "table": 30, "chair": 80}

# ---- Model ------------------------------------------------------
model = pulp.LpProblem("Product_Mix", pulp.LpMaximize)

make = model.add_variable_dict("make", products, lowBound=0)

model += pulp.lpSum(profit[p] * make[p] for p in products)

for r in resources:
    model += (pulp.lpSum(usage[r, p] * make[p] for p in products)
              <= capacity[r]), f"cap_{r}"

for p in products:
    model += make[p] <= max_demand[p], f"demand_{p}"

result = model.solve(pulp.HiGHS(msg=False))

# ---- Report -----------------------------------------------------
print("Status:", result.status_str)
for p in products:
    print(f"  {p:<6} {make[p].value():6.1f}")
print(f"Total profit: {pulp.value(model.objective):,.2f}")

"""The transportation problem: Tassili Cement (PuLP)."""
import pandas as pd
import pulp
from cement_data import plants, prod_cost, demand, ship_cost

P, C = list(plants), list(demand)
model = pulp.LpProblem("Tassili_Transport", pulp.LpMinimize)
x = model.add_variable_dict("ship", (P, C), lowBound=0)

model += pulp.lpSum((prod_cost[p] + ship_cost[p, c]) * x[p, c]
                    for p in P for c in C), "Total_cost"
for p in P:
    model += pulp.lpSum(x[p, c] for c in C) <= plants[p], f"supply_{p}"
for c in C:
    model += pulp.lpSum(x[p, c] for p in P) >= demand[c], f"demand_{c}"

result = model.solve(pulp.HiGHS(msg=False))
print("Status:", result.status_str)
plan = pd.DataFrame({c: {p: x[p, c].value() for p in P} for c in C})
print(plan.round(0).astype(int).to_string())
print(f"Total cost: ${pulp.value(model.objective):,.0f}")

used = {p: sum(x[p, c].value() for c in C) for p in P}
print("Plant use:", {p: f"{used[p]:.0f}/{plants[p]}" for p in P})
print("Marginal delivered cost per tonne ($):")
for k, c in enumerate(C):
    dual = abs(model.get_constraint_by_name(f"demand_{c}").pi)
    print(f"  {c:<12}{dual:6.2f}", end="\n" if k % 3 == 2 else "")
print()

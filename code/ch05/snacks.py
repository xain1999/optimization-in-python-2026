"""Solve the Sahara Snacks model and report the plan and bottlenecks."""
import pandas as pd
import pulp
from snacks_model import load_data, build_model, plan_table

data = load_data()
model, make = build_model(data)
result = model.solve(pulp.HiGHS(msg=False))

print("Status:", result.status_str)
print(plan_table(data, make))
print(f"Profit: {pulp.value(model.objective):,.0f}\n")

report = pd.DataFrame(
    [(c.name, c.slack + 0.0, abs(c.pi) + 0.0)     # magnitude: see Ch. 3
     for c in model.constraints()],
    columns=["constraint", "slack", "shadow_price"],
).set_index("constraint")
print(report[report["slack"].abs() < 1e-6].round(2))   # binding only

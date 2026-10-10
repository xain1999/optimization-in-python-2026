"""Two objectives in order: maximize profit, then minimize Annaba load."""
import pulp
from snacks_model import load_data, build_model, plan_table

data = load_data()
model, make = build_model(data)

profit = model.objective
annaba_hours = pulp.lpSum(data["hours"][p, k] * make[p, k]
                          for p, k in data["arcs"] if k == "Annaba")

# sequentialSolve keeps the sense of the model (maximize), so the second
# objective is negated: maximizing -hours means minimizing hours.
results = model.sequentialSolve([profit, -annaba_hours],
                                relativeTols=[0.99, 1.0],   # keep >= 99% of profit
                                solver=pulp.HiGHS(msg=False))

print("Statuses:", [r.status_str for r in results])
print(plan_table(data, make))
print(f"Profit: {pulp.value(profit):,.0f}   "
      f"Annaba hours: {pulp.value(annaba_hours):,.0f}")

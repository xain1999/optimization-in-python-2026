"""Scenario analysis: how much is extra capacity at Oran worth?"""
import pulp
from snacks_model import load_data, build_model

data = load_data()
print(f"{'Oran hours':>10} {'profit':>9} {'gain':>7}")
base = None
for hours in [900, 1000, 1100, 1200, 1300, 1400]:
    data["hours_avail"]["Oran"] = hours        # change the data ...
    model, make = build_model(data)            # ... and rebuild the model
    model.solve(pulp.HiGHS(msg=False))
    profit = pulp.value(model.objective)
    base = profit if base is None else base
    print(f"{hours:>10} {profit:>9,.0f} {profit - base:>7,.0f}")

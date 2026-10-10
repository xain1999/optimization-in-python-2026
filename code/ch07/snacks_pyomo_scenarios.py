"""Scenarios without rebuilding: change a mutable parameter, re-solve."""
import sys
sys.path.append("../ch05")
import pyomo.environ as pyo
from snacks_model import load_data
from snacks_pyomo import build_model

m = build_model(load_data("../ch05/data"))
solver = pyo.SolverFactory("appsi_highs")  # keeps a copy of the model

print(f"{'Oran hours':>10} {'profit':>9}")
for hours in [900, 1000, 1100, 1200, 1300, 1400]:
    m.hours_avail["Oran"] = hours            # update the parameter only
    solver.solve(m)                        # updated incrementally
    print(f"{hours:>10} {pyo.value(m.profit):>9,.0f}")

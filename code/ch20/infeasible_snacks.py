"""An infeasible Sahara Snacks model: find out why."""
import sys
sys.path.extend(["../ch05", "../ch07"])
from snacks_model import load_data
from snacks_pyomo import build_model
from diagnose import is_feasible, elastic_violations, conflict_set

data = load_data("../ch05/data")
data["min_dem"]["nachos"] = 600        # a new supermarket contract,
data["hours_avail"]["Algiers"] = 800   # maintenance at Algiers,
data["hours_avail"]["Oran"] = 0        # and Oran closed for renovation
m = build_model(data)

feasible = is_feasible(m)
print("Feasible:", feasible)
if feasible:
    raise SystemExit("Nothing to diagnose")
print("\n1. Elastic model - smallest total violation needed:")
for name, v in elastic_violations(m).items():
    print(f"   {name:<22} violated by {v:7.1f}")
print("\n2. Deletion filter - a minimal conflicting set:")
for name in conflict_set(m):
    print(f"   {name}")

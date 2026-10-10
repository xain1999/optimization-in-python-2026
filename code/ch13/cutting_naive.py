"""The 'assignment' formulation: which piece is cut from which bar."""
import math
import pulp
from rebar_data import bar_length, orders

L = list(orders)
need = sum(l * q for l, q in orders.items())
lower = math.ceil(need / bar_length)            # material lower bound
K = range(int(lower * 1.15))                    # bars we may use (enough)

m = pulp.LpProblem("Cutting_Naive", pulp.LpMinimize)
use = m.add_variable_dict("use", K, cat="Binary")
cut = m.add_variable_dict("cut", (L, K), lowBound=0, cat="Integer")

m += pulp.lpSum(use.values())
for l in L:                                     # cut every piece needed
    m += pulp.lpSum(cut[l, k] for k in K) >= orders[l]
for k in K:                                     # bar length
    m += pulp.lpSum(l * cut[l, k] for l in L) <= bar_length * use[k]

result = m.solve(pulp.HiGHS(msg=False, timeLimit=60))
print(f"Material lower bound: {lower} bars")
print(f"Naive model after 60 s: {result.status_str}, "
      f"{pulp.value(m.objective):.0f} bars")

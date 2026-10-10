"""Minimum-cost network flow (transshipment) in PuLP."""
import pulp
from network_data import arcs, supply

nodes = list(supply)
model = pulp.LpProblem("Transshipment", pulp.LpMinimize)
flow = {(i, j): model.add_variable(f"f_{i}_{j}", lowBound=0, upBound=cap)
        for (i, j), (cost, cap) in arcs.items()}

model += pulp.lpSum(arcs[a][0] * flow[a] for a in arcs)
for n in nodes:                                 # flow out - flow in = supply
    out_flow = pulp.lpSum(flow[i, j] for (i, j) in arcs if i == n)
    in_flow = pulp.lpSum(flow[i, j] for (i, j) in arcs if j == n)
    model += out_flow - in_flow == supply[n], f"balance_{n}"

model.solve(pulp.HiGHS(msg=False))
print(f"Total cost: ${pulp.value(model.objective):,.0f}")
for (i, j), f in flow.items():
    if f.value() > 0.5 and j != "excess":
        print(f"  {i:>12} -> {j:<12} {f.value():6.0f} t")

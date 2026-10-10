"""The same network solved with OR-Tools' minimum-cost-flow algorithm."""
from ortools.graph.python import min_cost_flow
from network_data import arcs, supply

nodes = list(supply)
index = {n: k for k, n in enumerate(nodes)}     # node names -> integers

mcf = min_cost_flow.SimpleMinCostFlow()
arc_ids = {}
for (i, j), (cost, cap) in arcs.items():        # costs in integer cents
    arc_ids[i, j] = mcf.add_arc_with_capacity_and_unit_cost(
        index[i], index[j], cap, round(cost * 100))
for n, s in supply.items():
    mcf.set_node_supply(index[n], s)

status = mcf.solve()
assert status == mcf.OPTIMAL, status
print(f"Total cost: ${mcf.optimal_cost() / 100:,.0f}")
moved = {a: mcf.flow(k) for a, k in arc_ids.items() if mcf.flow(k) > 0}
print(f"Arcs carrying flow: {len(moved)} (including unused capacity)")

"""Economic dispatch for one hour: the merit order and the market price."""
import pulp
from power_data import names, pmax, cost, demand, solar

hour = 20                                        # 20:00, the evening peak
load = demand[hour] - solar[hour]                # solar is used first

m = pulp.LpProblem("Dispatch", pulp.LpMinimize)
p = {u: m.add_variable(f"p_{u}", lowBound=0, upBound=pmax[u])
     for u in names}
m += pulp.lpSum(cost[u] * p[u] for u in names)
m += pulp.lpSum(p.values()) == load, "balance"
m.solve(pulp.HiGHS(msg=False))

print(f"Hour {hour}:00, net demand {load} MW")
for u in sorted(names, key=cost.get):
    print(f"  {u:<7} {cost[u]:>4} $/MWh  "
          f"{p[u].value():6.1f} of {pmax[u]} MW")
price = m.get_constraint_by_name("balance").pi
print(f"Cost ${pulp.value(m.objective):,.0f}/h, "
      f"marginal price {abs(price):.0f} $/MWh")

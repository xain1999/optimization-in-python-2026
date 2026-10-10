"""Tassili Cement with rail terminals: a transshipment network."""
import sys
sys.path.append("../common")
from geo import road_km
from cement_data import plants, prod_cost, demand, rate

# Terminal nodes get their own names: "Setif" is also a customer city, and
# one name for two nodes would merge them (and overwrite one of the arcs).
terminals = {"T-Blida": "Blida", "T-Setif": "Setif",
             "T-Mostaganem": "Mostaganem"}         # node: city it is in
rail_rate, handling, rail_cap = 0.025, 4.0, 1500   # $/t-km, $/t, t per link
BIG = 10 ** 6                                      # "unlimited" capacity

arcs = {}                                      # (i, j): (cost, capacity)
for p in plants:
    for c in demand:                               # direct by road
        arcs[p, c] = (prod_cost[p] + round(rate * road_km(p, c), 2), BIG)
    for t, city in terminals.items():              # by rail to a terminal
        arcs[p, t] = (prod_cost[p] + round(rail_rate * road_km(p, city), 2)
                      + handling, rail_cap)
    arcs[p, "excess"] = (0.0, BIG)                 # unused capacity
for t, city in terminals.items():
    for c in demand:                           # terminal -> city by road
        arcs[t, c] = (round(rate * road_km(city, c), 2), BIG)

# Every node name must be unique across plants, terminals and cities.
assert not set(plants) & set(terminals) and not set(terminals) & set(demand)

# Net supply: positive at plants, negative at cities, zero at terminals.
supply = {**plants, **{t: 0 for t in terminals},
          **{c: -d for c, d in demand.items()},
          "excess": -(sum(plants.values()) - sum(demand.values()))}

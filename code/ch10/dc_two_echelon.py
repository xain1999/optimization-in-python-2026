"""Two-echelon network design: factories -> centres -> cities (Pyomo)."""
import sys
sys.path.append("../common")
import pyomo.environ as pyo
from geo import road_km
import dc_data as d
from dc_model import build_model, solve, report

factories = {"Blida": 800, "Setif": 700}           # weekly capacity (t)
primary_rate = 0.07                                # $/t-km, full trucks

data = {"fixed": d.fixed, "capacity": d.capacity,
        "demand": d.demand, "cost": d.cost}
m = build_model(data, capacitated=True, single_source=True)

# Second echelon: tonnes shipped from each factory to each centre.
m.F = pyo.Set(initialize=list(factories))
m.supply = pyo.Var(m.F, m.S, domain=pyo.NonNegativeReals)

@m.Constraint(m.S)
def centre_balance(m, s):                          # inflow = outflow
    return (sum(m.supply[f, s] for f in m.F)
            == sum(d.demand[c] * m.serve[s, c] for c in m.C))

@m.Constraint(m.F)
def factory_capacity(m, f):
    return sum(m.supply[f, s] for s in m.S) <= factories[f]

m.primary_cost = pyo.Expression(expr=sum(
    primary_rate * road_km(f, s) * m.supply[f, s]
    for f in m.F for s in m.S))
m.total.expr = m.fixed_cost + m.transport_cost + m.primary_cost

opened, assign = solve(m)
report(m, data, opened)
print(f"+ factory-to-centre transport ${pyo.value(m.primary_cost):,.0f} "
      f"= total ${pyo.value(m.total):,.0f} per week")
for f in m.F:
    sent = {s: round(pyo.value(m.supply[f, s])) for s in m.S
            if pyo.value(m.supply[f, s]) > 0.5}
    print(f"  from {f}: {sent}")

# What if we had kept the single-echelon design and only then added
# factory transport? Fix the five centres of the capacitated design.
for s in m.S:
    m.open[s].fix(1 if s in ["Blida", "Oran", "Setif", "Batna", "Ghardaia"]
                  else 0)
solve(m)
print(f"Single-echelon design, full cost: ${pyo.value(m.total):,.0f}")

"""Capacitated facility location, with and without single sourcing."""
import pyomo.environ as pyo
import dc_data as d
from dc_model import build_model, solve, report

data = {"fixed": d.fixed, "capacity": d.capacity,
        "demand": d.demand, "cost": d.cost}

print("--- Capacitated, demand may be split ---")
m = build_model(data, capacitated=True)
opened, assign = solve(m)
report(m, data, opened)
split = [c for c in m.C
         if max(pyo.value(m.serve[s, c]) for s in m.S) < 0.999]
print("Cities supplied by two centres:", ", ".join(split) or "none")

print("\n--- Capacitated, single sourcing ---")
m = build_model(data, capacitated=True, single_source=True)
opened, assign = solve(m)
report(m, data, opened)

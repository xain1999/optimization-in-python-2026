"""Uncapacitated facility location for Mitidja Foods."""
import dc_data as d
from dc_model import build_model, solve, report

data = {"fixed": d.fixed, "capacity": d.capacity,
        "demand": d.demand, "cost": d.cost}
m = build_model(data)
opened, assign = solve(m)
report(m, data, opened)

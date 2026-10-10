"""Total weekly cost as a function of the number of open centres."""
import pyomo.environ as pyo
import dc_data as d
from dc_model import build_model, solve

data = {"fixed": d.fixed, "capacity": d.capacity,
        "demand": d.demand, "cost": d.cost}

rows = []
print(f"{'open':>4} {'uncapacitated':>14} {'capacitated':>12}")
for p in range(1, 9):
    m = build_model(data, n_open=p)
    solve(m)
    ufl = pyo.value(m.total)
    try:
        m = build_model(data, capacitated=True, single_source=True,
                        n_open=p)
        solve(m)
        cfl = pyo.value(m.total)
    except RuntimeError:              # too few centres to hold the demand
        cfl = float("nan")
    rows.append((p, ufl, cfl))
    cfl_txt = f"{cfl:12,.0f}" if cfl == cfl else f"{'infeasible':>12}"
    print(f"{p:>4} {ufl:14,.0f} {cfl_txt}")

with open("output/tradeoff.dat", "w") as f:    # data for the book's chart
    f.write("p ufl cfl\n")
    for p, ufl, cfl in rows:
        f.write(f"{p} {ufl:.0f} {cfl:.0f}\n" if cfl == cfl
                else f"{p} {ufl:.0f} nan\n")

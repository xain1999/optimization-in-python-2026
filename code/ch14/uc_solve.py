"""Solve the unit commitment model and print the schedule."""
import pyomo.environ as pyo
import power_data as d
from unit_commitment import build_model

m = build_model(commitment=True)
solver = pyo.SolverFactory("appsi_highs")
solver.config.mip_gap = 0.0001
solver.solve(m)

on = {(u, t): pyo.value(m.on[u, t]) > 0.5 for u in d.names for t in d.hours}
print("hour    " + "".join(f"{t % 10}" for t in d.hours) + "   start-ups")
for u in d.names:
    row = "".join("#" if on[u, t] else "." for t in d.hours)
    starts = round(sum(pyo.value(m.start[u, t]) for t in d.hours))
    print(f"{u:<8}{row}   {starts}")
pv = sum(pyo.value(m.pv[t]) for t in d.hours)
shed = sum(pyo.value(m.shed[t]) for t in d.hours)
print(f"Solar used {pv:,.0f} of {sum(d.solar):,} MWh; "
      f"unserved {shed:.0f} MWh")
print(f"Total cost: ${pyo.value(m.cost):,.0f}")

with open("output/uc_output.dat", "w") as f:       # data for the chart
    f.write("hour " + " ".join(d.names) + " Solar\n")
    for t in d.hours:
        mw = [pyo.value(m.p[u, t]) for u in d.names] + [pyo.value(m.pv[t])]
        f.write(f"{t} " + " ".join(f"{x:.1f}" for x in mw) + "\n")

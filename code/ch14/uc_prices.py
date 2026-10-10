"""LP relaxation, MILP, and hourly prices from the fixed commitment."""
import pyomo.environ as pyo
import power_data as d
from unit_commitment import build_model

solver = pyo.SolverFactory("appsi_highs")
solver.config.mip_gap = 0.0001

relaxed = build_model(commitment=False)          # on/off may be fractional
solver.solve(relaxed)
print(f"LP relaxation:        ${pyo.value(relaxed.cost):,.0f}")

m = build_model(commitment=True)
solver.solve(m)
print(f"Unit commitment MILP: ${pyo.value(m.cost):,.0f}")

# Fix every on/off decision at its optimal value; what is left is an LP
# whose balance-constraint duals are the hourly marginal energy prices.
for var in (m.on, m.start, m.stop):
    for idx in var:
        var[idx].fix(round(pyo.value(var[idx])))
        var[idx].domain = pyo.UnitInterval      # no longer integer: an LP
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
pyo.SolverFactory("appsi_highs").solve(m)
prices = [m.dual[m.balance[t]] for t in d.hours]

print("Marginal price ($/MWh) by hour:")
for k in range(0, 24, 6):
    print("  " + "  ".join(f"{t:02d}h {prices[t]:4.0f}"
                           for t in d.hours[k:k + 6]))
with open("output/prices.dat", "w") as f:
    f.write("hour price demand\n")
    for t in d.hours:
        f.write(f"{t} {prices[t]:.2f} {d.demand[t]}\n")

"""Efficient frontiers: minimum CVaR and minimum MAD for each target."""
import numpy as np
from returns_data import assets, returns as R
from portfolio_models import solve_portfolio, cvar

mean = R.mean(axis=0)
lo, hi = 0.48, 1.02                               # targets, % per month
rows = []
print(f"{'target %/mo':>11}{'CVaR95':>8}{'MAD':>7}{'stdev':>7}   "
      "largest holdings (min-CVaR)")
for target in np.linspace(lo, hi, 10):
    w_c, obj_c = solve_portfolio(R, assets, target, risk="cvar")
    w_m, obj_m = solve_portfolio(R, assets, target, risk="mad")
    if w_c is None:
        continue
    top = sorted(zip(w_c, assets), reverse=True)[:3]
    print(f"{target:>11.2f}{obj_c:>8.2f}{obj_m:>7.2f}"
          f"{(R @ w_c).std():>7.2f}   "
          + ", ".join(f"{a} {x:.0%}" for x, a in top if x > 0.005))
    rows.append((target, obj_c, obj_m, (R @ w_m).std()))
with open("output/frontier.dat", "w") as f:
    f.write("target cvar mad std_mad\n")
    for r in rows:
        f.write(" ".join(f"{v:.4f}" for v in r) + "\n")

"""Practical constraints: few holdings, minimum sizes, limited turnover."""
import numpy as np
import pulp
from returns_data import assets, returns as R
from portfolio_models import solve_portfolio

current = dict(zip(assets, [0.10] * 10))           # today: equal weights
target = 0.80                                      # % per month


def realistic(m, w):
    hold = m.add_variable_dict("hold", assets, cat="Binary")
    buy = m.add_variable_dict("buy", assets, lowBound=0)
    sell = m.add_variable_dict("sell", assets, lowBound=0)
    for a in assets:
        m += w[a] <= 0.30 * hold[a], f"only_if_held_{a}"
        m += w[a] >= 0.05 * hold[a], f"min_size_{a}"
        m += w[a] - current[a] == buy[a] - sell[a], f"trade_{a}"
    m += pulp.lpSum(hold.values()) <= 6, "at_most_6_assets"
    m += pulp.lpSum(buy.values()) <= 0.45, "turnover"   # trade <= 45%


for label, extra in [("LP (no extra rules)", None),
                     ("with practical rules", realistic)]:
    w, risk = solve_portfolio(R, assets, target, risk="cvar", extra=extra)
    held = [(a, x) for a, x in zip(assets, w) if x > 1e-4]
    print(f"{label}: CVaR95 {risk:.2f}%, {len(held)} assets")
    print("   " + ", ".join(f"{a} {x:.0%}" for a, x in held))
    traded = sum(abs(x - current[a]) for a, x in zip(assets, w)) / 2
    print(f"   one-way turnover from current portfolio: {traded:.0%}")

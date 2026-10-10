"""Do optimized portfolios keep their promises? Fit 7 years, test 3."""
import numpy as np
from returns_data import assets, returns as R
from portfolio_models import solve_portfolio, cvar

train, test = R[:84], R[84:]
n = len(assets)
# Highest mean achievable with weights capped at 30%: 30/30/30/10.
best = np.sort(train.mean(axis=0))[::-1][:4] @ [0.3, 0.3, 0.3, 0.1]
candidates = {
    "Equal weights": np.full(n, 1 / n),
    "Min CVaR": solve_portfolio(train, assets, target=-100)[0],
    "CVaR, target 0.8%": solve_portfolio(train, assets, target=0.8)[0],
    "99% of max return": solve_portfolio(train, assets,
                                         target=0.99 * best)[0],
}
print(f"{'portfolio':<18}{'--- training (84 mo) ---':>26}"
      f"{'---- test (36 mo) ----':>26}")
print(f"{'':<18}{'mean':>8}{'CVaR95':>9}{'worst':>8}"
      f"   {'mean':>8}{'CVaR95':>9}{'worst':>8}")
for name, w in candidates.items():
    a, b = train @ w, test @ w
    print(f"{name:<18}{a.mean():>8.2f}{cvar(a):>9.2f}{a.min():>8.1f}"
          f"   {b.mean():>8.2f}{cvar(b):>9.2f}{b.min():>8.1f}")

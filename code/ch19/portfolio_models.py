"""Mean-absolute-deviation and CVaR portfolio models as LPs (PuLP)."""
import numpy as np
import pulp


def solve_portfolio(R, assets, target, risk="cvar", beta=0.95,
                    max_weight=0.30, extra=None):
    """Minimize risk subject to an expected monthly return >= target (%).

    R is a (T x n) array of scenario returns in % per month. `extra` may
    be a function(model, w) that adds further constraints.
    """
    T, n = R.shape
    mean = R.mean(axis=0)
    m = pulp.LpProblem("Portfolio", pulp.LpMinimize)
    w = m.add_variable_dict("w", assets, lowBound=0, upBound=max_weight)
    port = [pulp.lpSum(float(R[t, i]) * w[a] for i, a in enumerate(assets))
            for t in range(T)]                       # scenario returns

    m += pulp.lpSum(w.values()) == 1, "budget"
    m += (pulp.lpSum(float(mean[i]) * w[a] for i, a in enumerate(assets))
          >= target, "target")
    if risk == "mad":       # mean absolute deviation: d_t >= |r_t - mean|
        exp = pulp.lpSum(float(mean[i]) * w[a]
                         for i, a in enumerate(assets))
        d = m.add_variable_dict("d", range(T), lowBound=0)
        for t in range(T):
            m += d[t] >= port[t] - exp
            m += d[t] >= exp - port[t]
        m += pulp.lpSum(d.values()) / T
    else:                   # CVaR of losses (Rockafellar and Uryasev)
        var = m.add_variable("VaR")                  # free variable
        z = m.add_variable_dict("z", range(T), lowBound=0)
        for t in range(T):
            m += z[t] >= -port[t] - var             # loss beyond VaR
        m += var + pulp.lpSum(z.values()) / ((1 - beta) * T)
    if extra:
        extra(m, w)
    result = m.solve(pulp.HiGHS(msg=False))
    if result.status_str != "Optimal":
        return None, None
    weights = np.array([w[a].value() for a in assets])
    return weights, pulp.value(m.objective)


def cvar(returns, beta=0.95):
    """Average loss in the worst (1 - beta) share of equally likely
    scenarios. When (1 - beta) * T is not a whole number, the boundary
    scenario counts with a fractional weight, exactly as in the LP."""
    r = np.asarray(returns, dtype=float)
    if r.ndim != 1 or r.size == 0 or not 0 <= beta < 1:
        raise ValueError("need a nonempty 1-D array and 0 <= beta < 1")
    losses = np.sort(-r)[::-1]                  # largest loss first
    q = (1 - beta) * r.size                     # tail size, e.g. 4.2
    k = int(np.floor(q))
    total = losses[:k].sum()
    if k < r.size:
        total += (q - k) * losses[k]            # fractional boundary term
    return float(total / q)

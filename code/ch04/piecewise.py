"""Incremental quantity discounts: a piecewise-linear cost with binaries."""
import pulp

# Price tiers for wood (board-metres): each price applies only to the
# units bought within that tier.
tier_size  = [300, 300, 1000]      # widths of tiers 1, 2, 3
tier_price = [5.0, 4.0, 3.0]       # $ per board-metre in each tier
need = 650
T = range(len(tier_size))

def solve(use_binaries):
    m = pulp.LpProblem("Wood_Purchase", pulp.LpMinimize)
    q = [m.add_variable(f"q{t}", lowBound=0, upBound=tier_size[t])
         for t in T]
    m += pulp.lpSum(tier_price[t] * q[t] for t in T)
    m += pulp.lpSum(q) >= need, "Need"
    if use_binaries:
        # y[t] = 1 if tier t is "reached".  A tier may be used only if it
        # is reached, and reaching tier t+1 requires tier t to be full.
        y = [m.add_variable(f"y{t}", cat="Binary") for t in T]
        for t in T:
            m += q[t] <= tier_size[t] * y[t], f"use_{t}"
        for t in T[:-1]:
            m += q[t] >= tier_size[t] * y[t + 1], f"fill_{t}"
    m.solve(pulp.HiGHS(msg=False))
    return [qt.value() for qt in q], pulp.value(m.objective)

for flag in (False, True):
    q, cost = solve(flag)
    label = "with binaries   " if flag else "LP (no binaries)"
    print(f"{label}: tiers = {[round(v) for v in q]}, cost = ${cost:,.0f}")

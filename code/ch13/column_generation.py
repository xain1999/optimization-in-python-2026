"""Cutting stock by column generation (Gilmore-Gomory)."""
import math
import pulp
from rebar_data import bar_length, orders

L = list(orders)


def knapsack(values, W):
    """Most valuable pattern fitting in length W (dynamic programming)."""
    best = [0.0] * (W + 1)                 # best[w]: value using length w
    choice = [None] * (W + 1)
    for w in range(1, W + 1):
        best[w], choice[w] = best[w - 1], None
        for l in L:
            if l <= w and best[w - l] + values[l] > best[w] + 1e-9:
                best[w], choice[w] = best[w - l] + values[l], l
    pattern, w = {l: 0 for l in L}, W           # rebuild the best pattern
    while w > 0:
        if choice[w] is None:
            w -= 1
        else:
            pattern[choice[w]] += 1
            w -= choice[w]
    return best[W], pattern


def master(patterns, integer=False):
    m = pulp.LpProblem("Master", pulp.LpMinimize)
    cat = "Integer" if integer else "Continuous"
    x = m.add_variable_dict("x", range(len(patterns)), lowBound=0, cat=cat)
    m += pulp.lpSum(x.values())
    for l in L:
        m += (pulp.lpSum(p[l] * x[j] for j, p in enumerate(patterns))
              >= orders[l], f"demand_{l}")
    m.solve(pulp.HiGHS(msg=False))
    duals = {} if integer else {
        l: m.get_constraint_by_name(f"demand_{l}").pi for l in L}
    values = [v.value() for v in x.values()]    # read before m disappears
    return pulp.value(m.objective), values, duals


# Start with one simple pattern per length: as many pieces as fit.
patterns = [{l: (bar_length // l if l == k else 0) for l in L} for k in L]

for it in range(1, 100):
    lp_value, x, duals = master(patterns)
    value, pattern = knapsack(duals, bar_length)
    print(f"iteration {it:2}: LP = {lp_value:8.3f} bars, "
          f"best new pattern value = {value:.3f}")
    if value <= 1 + 1e-9:            # no pattern has negative reduced cost
        break
    patterns.append(pattern)

ip_value, x, _ = master(patterns, integer=True)
print(f"\nLP bound: {lp_value:.3f}, so at least "
      f"{math.ceil(lp_value - 1e-9)} bars are needed")
print(f"Integer solution with {len(patterns)} patterns: "
      f"{ip_value:.0f} bars")
for j, p in enumerate(patterns):
    n = round(x[j])
    if n:
        pieces = " + ".join(f"{c}x{l}" for l, c in p.items() if c)
        waste = bar_length - sum(l * c for l, c in p.items())
        unit = "bar: " if n == 1 else "bars:"
        print(f"  {n:3} {unit} {pieces:<28} waste {waste:3} cm")

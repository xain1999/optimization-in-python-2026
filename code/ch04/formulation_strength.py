"""Weak versus strong formulations of the same facility-location model."""
import random
import time
import pulp

random.seed(7)
F = range(25)                              # candidate facilities
C = range(80)                              # customers
fixed = {f: random.randint(1500, 3000) for f in F}
fx = {f: (random.random(), random.random()) for f in F}
cx = {c: (random.random(), random.random()) for c in C}
cost = {(f, c): round(1000 * ((fx[f][0] - cx[c][0]) ** 2 +
                              (fx[f][1] - cx[c][1]) ** 2) ** 0.5)
        for f in F for c in C}

def build(strong, relax):
    cat = "Continuous" if relax else "Binary"
    m = pulp.LpProblem("Facility_Location", pulp.LpMinimize)
    open_ = {f: m.add_variable(f"open_{f}", lowBound=0, upBound=1, cat=cat)
             for f in F}
    x = {(f, c): m.add_variable(f"x_{f}_{c}", lowBound=0, upBound=1)
         for f in F for c in C}
    m += (pulp.lpSum(fixed[f] * open_[f] for f in F)
          + pulp.lpSum(cost[f, c] * x[f, c] for f in F for c in C))
    for c in C:                            # every customer is served
        m += pulp.lpSum(x[f, c] for f in F) == 1
    if strong:                             # one link per (f, c) pair
        for f in F:
            for c in C:
                m += x[f, c] <= open_[f]
    else:                                  # one aggregated link per f
        for f in F:
            m += pulp.lpSum(x[f, c] for c in C) <= len(C) * open_[f]
    return m

print(f"{'Formulation':<12}{'LP bound':>10}{'MILP opt':>10}"
      f"{'gap':>7}{'time (s)':>10}")
for strong in (False, True):
    lp = build(strong, relax=True)
    lp.solve(pulp.HiGHS(msg=False))
    ip = build(strong, relax=False)
    t0 = time.perf_counter()
    ip.solve(pulp.HiGHS(msg=False))
    dt = time.perf_counter() - t0
    lb, opt = pulp.value(lp.objective), pulp.value(ip.objective)
    name = "strong" if strong else "weak"
    print(f"{name:<12}{lb:10,.0f}{opt:10,.0f}{(opt - lb) / opt:7.1%}"
          f"{dt:10.2f}")

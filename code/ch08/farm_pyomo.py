"""Farm planning in Pyomo."""
import time
import pyomo.environ as pyo


def solve(d, time_limit=120):
    t0 = time.perf_counter()
    m = pyo.ConcreteModel(name="Farm")
    m.F = pyo.Set(initialize=d["fields"])
    m.C = pyo.Set(initialize=d["crops"])
    m.M = pyo.Set(initialize=d["months"])
    a = d["area"]

    m.y = pyo.Var(m.F, m.C, domain=pyo.Binary)
    m.z = pyo.Var(m.C, domain=pyo.Binary)

    @m.Objective(sense=pyo.maximize)
    def revenue(m):
        return sum(d["revenue"][f, c] * m.y[f, c] for f in m.F for c in m.C)

    @m.Constraint(m.F)
    def one_crop(m, f):
        return sum(m.y[f, c] for c in m.C) <= 1

    @m.Constraint(m.M)
    def water(m, mo):
        return sum(a[f] * d["water"][c, mo] * m.y[f, c]
                   for f in m.F for c in m.C) <= d["water_cap"][mo]

    @m.Constraint(m.M)
    def labour(m, mo):
        return sum(a[f] * d["labour"][c, mo] * m.y[f, c]
                   for f in m.F for c in m.C) <= d["labour_cap"][mo]

    @m.Constraint(m.C)
    def market(m, c):
        return sum(a[f] * m.y[f, c] for f in m.F) <= d["market"][c]

    @m.Constraint(m.F, m.C)
    def link(m, f, c):
        return m.y[f, c] <= m.z[c]

    @m.Constraint(m.C)
    def grown(m, c):                   # z[c] = 1 only if c is planted
        return m.z[c] <= sum(m.y[f, c] for f in m.F)

    @m.Constraint()
    def diversity(m):
        return sum(m.z[c] for c in m.C) >= d["min_crops"]
    t1 = time.perf_counter()

    solver = pyo.SolverFactory("appsi_highs")
    solver.config.time_limit = time_limit
    result = solver.solve(m, load_solutions=False)
    t2 = time.perf_counter()
    cond = result.solver.termination_condition
    if cond not in (pyo.TerminationCondition.optimal,
                    pyo.TerminationCondition.maxTimeLimit):
        raise RuntimeError(f"No usable solution: {cond}")
    m.solutions.load_from(result)               # fails if none was found
    plan = {f: c for f in m.F for c in m.C if pyo.value(m.y[f, c]) > 0.5}
    return pyo.value(m.revenue), plan, t1 - t0, t2 - t1


if __name__ == "__main__":
    from farm_data import small
    obj, plan, tb, ts = solve(small())
    print(f"Net revenue: ${obj:,.0f}")
    for f, c in sorted(plan.items()):
        print(f"  {f}: {c}")

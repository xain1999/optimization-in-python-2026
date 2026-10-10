"""Farm planning with OR-Tools' linear solver interface (SCIP)."""
import time
from ortools.linear_solver import pywraplp


def solve(d, time_limit=120, engine="SCIP"):
    t0 = time.perf_counter()
    F, C, M, a = d["fields"], d["crops"], d["months"], d["area"]

    solver = pywraplp.Solver.CreateSolver(engine)
    y = {(f, c): solver.BoolVar(f"plant_{f}_{c}") for f in F for c in C}
    z = {c: solver.BoolVar(f"grow_{c}") for c in C}

    solver.Maximize(sum(d["revenue"][f, c] * y[f, c] for f in F for c in C))
    for f in F:
        solver.Add(sum(y[f, c] for c in C) <= 1, f"one_crop_{f}")
    for m in M:
        solver.Add(sum(a[f] * d["water"][c, m] * y[f, c]
                       for f in F for c in C) <= d["water_cap"][m])
        solver.Add(sum(a[f] * d["labour"][c, m] * y[f, c]
                       for f in F for c in C) <= d["labour_cap"][m])
    for c in C:
        solver.Add(sum(a[f] * y[f, c] for f in F) <= d["market"][c])
        for f in F:
            solver.Add(y[f, c] <= z[c])
        solver.Add(z[c] <= sum(y[f, c] for f in F))   # grown somewhere
    solver.Add(sum(z.values()) >= d["min_crops"])
    t1 = time.perf_counter()

    solver.SetTimeLimit(int(time_limit * 1000))
    status = solver.Solve()
    t2 = time.perf_counter()
    if status not in (solver.OPTIMAL, solver.FEASIBLE):
        raise RuntimeError(f"No usable solution: status {status}")
    plan = {f: c for f in F for c in C if y[f, c].solution_value() > 0.5}
    return solver.Objective().Value(), plan, t1 - t0, t2 - t1


if __name__ == "__main__":
    from farm_data import small
    obj, plan, tb, ts = solve(small())
    print(f"Net revenue: ${obj:,.0f}")
    for f, c in sorted(plan.items()):
        print(f"  {f}: {c}")

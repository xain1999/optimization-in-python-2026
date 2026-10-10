"""Farm planning in PuLP."""
import time
import pulp


def solve(d, time_limit=120):
    t0 = time.perf_counter()
    F, C, M, a = d["fields"], d["crops"], d["months"], d["area"]

    model = pulp.LpProblem("Farm", pulp.LpMaximize)
    y = model.add_variable_dict("plant", (F, C), cat="Binary")
    z = model.add_variable_dict("grow", C, cat="Binary")

    model += pulp.lpSum(d["revenue"][f, c] * y[f, c] for f in F for c in C)
    for f in F:
        model += pulp.lpSum(y[f, c] for c in C) <= 1, f"one_crop_{f}"
    for m in M:
        model += (pulp.lpSum(a[f] * d["water"][c, m] * y[f, c]
                             for f in F for c in C)
                  <= d["water_cap"][m]), f"water_{m}"
        model += (pulp.lpSum(a[f] * d["labour"][c, m] * y[f, c]
                             for f in F for c in C)
                  <= d["labour_cap"][m]), f"labour_{m}"
    for c in C:
        model += (pulp.lpSum(a[f] * y[f, c] for f in F)
                  <= d["market"][c]), f"market_{c}"
        for f in F:
            model += y[f, c] <= z[c], f"link_{f}_{c}"
        # z[c] = 1 only if crop c is really planted on some field
        model += z[c] <= pulp.lpSum(y[f, c] for f in F), f"grown_{c}"
    model += pulp.lpSum(z.values()) >= d["min_crops"], "diversity"
    t1 = time.perf_counter()

    result = model.solve(pulp.HiGHS(msg=False, timeLimit=time_limit))
    t2 = time.perf_counter()
    if not result.has_solution:                 # infeasible, or no solution
        raise RuntimeError(f"No usable solution: {result.status_str}")
    plan = {f: c for f in F for c in C if y[f, c].value() > 0.5}
    return pulp.value(model.objective), plan, t1 - t0, t2 - t1


if __name__ == "__main__":
    from farm_data import small
    obj, plan, tb, ts = solve(small())
    print(f"Net revenue: ${obj:,.0f}")
    for f, c in sorted(plan.items()):
        print(f"  {f}: {c}")

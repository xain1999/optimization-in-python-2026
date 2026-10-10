"""How fast are specialized assignment algorithms? Random n x n costs."""
import time
import numpy as np
import pulp
from ortools.graph.python import linear_sum_assignment
from scipy.optimize import linear_sum_assignment as scipy_lsa

rng = np.random.default_rng(42)
print(f"{'n':>6}{'LP (HiGHS)':>12}{'OR-Tools':>11}{'SciPy':>9}   seconds")
for n in [100, 300, 1000, 3000]:
    cost = rng.integers(1, 1000, size=(n, n))
    if n <= 300:                              # the LP gets large quickly
        t = time.perf_counter()
        m = pulp.LpProblem("A", pulp.LpMinimize)
        x = m.add_variable_dict("x", (range(n), range(n)), lowBound=0)
        m += pulp.lpSum(int(cost[i, j]) * x[i, j]
                        for i in range(n) for j in range(n))
        for i in range(n):
            m += pulp.lpSum(x[i, j] for j in range(n)) == 1
            m += pulp.lpSum(x[j, i] for j in range(n)) == 1
        m.solve(pulp.HiGHS(msg=False))
        lp_time = time.perf_counter() - t
    t = time.perf_counter()
    lsa = linear_sum_assignment.SimpleLinearSumAssignment()
    lsa.add_arcs_with_cost(np.repeat(np.arange(n), n), np.tile(np.arange(n), n),
                           cost.ravel())
    lsa.solve()
    ort_time = time.perf_counter() - t
    t = time.perf_counter()
    r, c = scipy_lsa(cost)
    sp_time = time.perf_counter() - t
    assert lsa.optimal_cost() == cost[r, c].sum()
    lp = f"{lp_time:.2f}" if n <= 300 else "-"
    print(f"{n:>6}{lp:>12}{ort_time:>11.2f}{sp_time:>9.2f}")

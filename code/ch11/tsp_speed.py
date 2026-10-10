"""Exact MILP (MTZ) versus the routing library as the TSP grows."""
import math
import random
import time
import pulp
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def random_points(n, seed):
    rng = random.Random(seed)
    pts = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]
    return [[round(10 * math.dist(a, b)) for b in pts] for a in pts]


def mtz(d, limit):
    n = len(d)
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    m = pulp.LpProblem("TSP", pulp.LpMinimize)
    x = m.add_variable_dict("x_%s_%s", arcs, cat="Binary")
    u = m.add_variable_dict("u", range(1, n), lowBound=1, upBound=n - 1)
    m += pulp.lpSum(d[i][j] * x[i, j] for i, j in arcs)
    for k in range(n):
        m += pulp.lpSum(x[i, k] for i in range(n) if i != k) == 1
        m += pulp.lpSum(x[k, j] for j in range(n) if j != k) == 1
    for i, j in arcs:
        if i and j:
            m += u[i] - u[j] + (n - 1) * x[i, j] <= n - 2
    r = m.solve(pulp.HiGHS(msg=False, timeLimit=limit))
    return pulp.value(m.objective), r.status_str


def routing(d, limit):
    mgr = pywrapcp.RoutingIndexManager(len(d), 1, 0)
    rm = pywrapcp.RoutingModel(mgr)
    cb = rm.RegisterTransitCallback(
        lambda a, b: d[mgr.IndexToNode(a)][mgr.IndexToNode(b)])
    rm.SetArcCostEvaluatorOfAllVehicles(cb)
    p = pywrapcp.DefaultRoutingSearchParameters()
    p.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    p.time_limit.FromSeconds(limit)
    return rm.SolveWithParameters(p).ObjectiveValue()


print(f"{'n':>4}{'MILP':>9}{'status':>11}{'time':>7}"
      f"{'routing':>9}{'time':>6}")
for n in [15, 30, 60, 100]:
    d = random_points(n, seed=n)
    t = time.perf_counter(); z, st = mtz(d, limit=60)
    t1 = time.perf_counter() - t
    t = time.perf_counter(); r = routing(d, limit=5)
    t2 = time.perf_counter() - t
    print(f"{n:>4}{z:>9,.0f}{st:>11}{t1:>7.1f}{r:>9,}{t2:>6.1f}")

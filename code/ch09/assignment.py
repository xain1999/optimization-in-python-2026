"""Assigning technicians to jobs: LP, OR-Tools and SciPy."""
import numpy as np
import pulp
from ortools.graph.python import linear_sum_assignment
from scipy.optimize import linear_sum_assignment as scipy_lsa

techs = ["Amina", "Bilal", "Chahra", "Djamel", "Elyes", "Farah"]
jobs = ["J1", "J2", "J3", "J4", "J5", "J6"]
hours = np.array([            # estimated hours for technician i on job j
    [9, 6, 11, 8, 7, 10],
    [7, 8, 10, 6, 9, 12],
    [10, 7, 8, 9, 6, 9],
    [6, 9, 12, 7, 8, 11],
    [8, 10, 7, 10, 9, 8],
    [11, 8, 9, 7, 10, 6],
])
n = len(techs)

# 1. As a linear program (no integer restriction!)
m = pulp.LpProblem("Assignment", pulp.LpMinimize)
x = m.add_variable_dict("x", (range(n), range(n)), lowBound=0)
m += pulp.lpSum(int(hours[i, j]) * x[i, j] for i in range(n) for j in range(n))
for i in range(n):
    m += pulp.lpSum(x[i, j] for j in range(n)) == 1, f"tech_{i}"
for j in range(n):
    m += pulp.lpSum(x[i, j] for i in range(n)) == 1, f"job_{j}"
m.solve(pulp.HiGHS(msg=False))
lp_pairs = [(i, j) for i in range(n) for j in range(n) if x[i, j].value() > 0.5]
fractional = [v.value() for v in x.values() if 1e-6 < v.value() < 1 - 1e-6]
print(f"LP:       {pulp.value(m.objective):.0f} hours, "
      f"fractional values: {len(fractional)}")

# 2. OR-Tools' specialized assignment algorithm
lsa = linear_sum_assignment.SimpleLinearSumAssignment()
for i in range(n):
    for j in range(n):
        lsa.add_arc_with_cost(i, j, int(hours[i, j]))
assert lsa.solve() == lsa.OPTIMAL
print(f"OR-Tools: {lsa.optimal_cost()} hours")

# 3. SciPy (Hungarian-type algorithm on a NumPy matrix)
rows, cols = scipy_lsa(hours)
print(f"SciPy:    {hours[rows, cols].sum()} hours")
for i, j in zip(rows, cols):
    print(f"  {techs[i]:<7} -> {jobs[j]}  ({hours[i, j]} h)")

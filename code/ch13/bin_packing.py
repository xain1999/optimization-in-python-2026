"""Bin packing: jobs into 8-hour machine shifts. Heuristic vs CP-SAT."""
import random
import time
from ortools.sat.python import cp_model

random.seed(5)
jobs = [random.randint(110, 190) for _ in range(60)]    # minutes
shift = 480                                            # minutes per shift
print(f"{len(jobs)} jobs, {sum(jobs)} minutes in total; "
      f"lower bound {-(-sum(jobs) // shift)} shifts")

# 1. First-fit decreasing: longest job first, into the first shift with room.
t = time.perf_counter()
loads = []
for d in sorted(jobs, reverse=True):
    for k, load in enumerate(loads):
        if load + d <= shift:
            loads[k] += d
            break
    else:
        loads.append(d)
print(f"First-fit decreasing: {len(loads)} shifts "
      f"({time.perf_counter() - t:.3f} s)")

# 2. CP-SAT, with at most as many shifts as the heuristic needed.
t = time.perf_counter()
n, B = len(jobs), len(loads)
m = cp_model.CpModel()
x = {(i, b): m.new_bool_var(f"x{i}_{b}") for i in range(n) for b in range(B)}
used = [m.new_bool_var(f"used{b}") for b in range(B)]
for i in range(n):
    m.add_exactly_one(x[i, b] for b in range(B))
for b in range(B):
    m.add(sum(jobs[i] * x[i, b] for i in range(n)) <= shift * used[b])
    if b > 0:
        m.add(used[b] <= used[b - 1])               # symmetry breaking
m.minimize(sum(used))
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
solver.parameters.num_workers = 8
status = solver.solve(m)
print(f"CP-SAT: {solver.objective_value:.0f} shifts, "
      f"{solver.status_name(status)} ({time.perf_counter() - t:.1f} s)")

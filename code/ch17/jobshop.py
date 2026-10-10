"""The job-shop problem ft06 (Fisher and Thompson, 1963) with CP-SAT."""
from ortools.sat.python import cp_model

# Each job is a sequence of (machine, duration) operations, done in order.
jobs = [
    [(2, 1), (0, 3), (1, 6), (3, 7), (5, 3), (4, 6)],
    [(1, 8), (2, 5), (4, 10), (5, 10), (0, 10), (3, 4)],
    [(2, 5), (3, 4), (5, 8), (0, 9), (1, 1), (4, 7)],
    [(1, 5), (0, 5), (2, 5), (3, 3), (4, 8), (5, 9)],
    [(2, 9), (1, 3), (4, 5), (5, 4), (0, 3), (3, 1)],
    [(1, 3), (3, 3), (5, 9), (0, 10), (4, 4), (2, 1)],
]
machines = range(6)
horizon = sum(d for job in jobs for _, d in job)    # a safe upper bound

m = cp_model.CpModel()
start, end, interval = {}, {}, {}
for j, job in enumerate(jobs):
    for k, (mach, dur) in enumerate(job):
        start[j, k] = m.new_int_var(0, horizon, f"s{j}_{k}")
        end[j, k] = m.new_int_var(0, horizon, f"e{j}_{k}")
        interval[j, k] = m.new_interval_var(start[j, k], dur, end[j, k],
                                            f"op{j}_{k}")
    for k in range(len(job) - 1):                     # operations in order
        m.add(start[j, k + 1] >= end[j, k])

for mach in machines:                                 # one job at a time
    m.add_no_overlap(interval[j, k] for j, job in enumerate(jobs)
                     for k, (mm, _) in enumerate(job) if mm == mach)

makespan = m.new_int_var(0, horizon, "makespan")
m.add_max_equality(makespan, [end[j, len(job) - 1]
                              for j, job in enumerate(jobs)])
m.minimize(makespan)

solver = cp_model.CpSolver()
solver.parameters.num_workers = 8
status = solver.solve(m)
print(f"Status: {solver.status_name(status)}, "
      f"makespan {solver.value(makespan)}")
for mach in machines:
    ops = sorted((solver.value(start[j, k]), j, d)
                 for j, job in enumerate(jobs)
                 for k, (mm, d) in enumerate(job) if mm == mach)
    print(f"Machine {mach}: " + "  ".join(f"J{j}[{s}-{s + d}]"
                                         for s, j, d in ops))
with open("output/jobshop.dat", "w") as f:       # data for the Gantt chart
    for j, job in enumerate(jobs):
        for k, (mach, d) in enumerate(job):
            f.write(f"{mach} {j} {solver.value(start[j, k])} {d}\n")

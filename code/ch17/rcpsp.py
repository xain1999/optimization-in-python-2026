"""Resource-constrained project scheduling with CP-SAT."""
from ortools.sat.python import cp_model
from project_data import activities, masons_available

A = list(activities)
horizon = sum(v[1] for v in activities.values())

m = cp_model.CpModel()
start = {a: m.new_int_var(0, horizon, f"s_{a}") for a in A}
end = {a: m.new_int_var(0, horizon, f"e_{a}") for a in A}
task = {a: m.new_interval_var(start[a], activities[a][1], end[a], a)
        for a in A}

for a in A:
    for p in activities[a][2]:
        m.add(start[a] >= end[p])                         # precedence

masons = [a for a in A if activities[a][3] > 0]
m.add_cumulative([task[a] for a in masons],               # mason crew
                 [activities[a][3] for a in masons], masons_available)
m.add_no_overlap(task[a] for a in A if activities[a][4])  # one crane

finish = m.new_int_var(0, horizon, "finish")
m.add_max_equality(finish, [end[a] for a in A])
m.minimize(finish)

solver = cp_model.CpSolver()
status = solver.solve(m)
print(f"Status: {solver.status_name(status)}, "
      f"duration {solver.value(finish)} working days")
for a in sorted(A, key=lambda a: solver.value(start[a])):
    s, d = solver.value(start[a]), activities[a][1]
    crew = activities[a][3]
    print(f"  {a} {activities[a][0]:<24} days {s:3}-{s + d:<3}"
          f"{'  masons ' + str(crew) if crew else ''}")
with open("output/rcpsp.dat", "w") as f:                  # for the chart
    for a in A:
        f.write(f"{a} {solver.value(start[a])} {activities[a][1]} "
                f"{activities[a][3]}\n")

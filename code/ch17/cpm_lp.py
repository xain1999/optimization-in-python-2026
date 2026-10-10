"""Critical path method as a linear program (PuLP)."""
import pulp
from project_data import activities

A = list(activities)
dur = {a: activities[a][1] for a in A}
pred = {a: activities[a][2] for a in A}

m = pulp.LpProblem("CPM", pulp.LpMinimize)
start = m.add_variable_dict("start", A, lowBound=0)
finish = m.add_variable("finish", lowBound=0)
m += finish                                          # project duration
for a in A:
    for p in pred[a]:                                # a starts after p ends
        m += start[a] >= start[p] + dur[p], f"prec_{p}_{a}"
    m += finish >= start[a] + dur[a], f"end_{a}"
m.solve(pulp.HiGHS(msg=False))

print(f"Project duration: {pulp.value(finish):.0f} working days")
critical = [c.name for c in m.constraints() if abs(c.pi) > 1e-6]
path = [name.split("_")[1] for name in critical]   # "prec_A_B" -> "A"
print("Precedences with dual value 1 form the critical path:")
print("  " + " -> ".join(path))
for a in A:
    print(f"  {a} {activities[a][0]:<24} start day "
          f"{start[a].value():4.0f}")

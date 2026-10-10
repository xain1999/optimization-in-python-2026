"""Exam timetabling: hard conflicts, seat limits and same-day penalties."""
from ortools.sat.python import cp_model
from exam_data import courses, size, shared, slots, seats, unavailable

m = cp_model.CpModel()
slot = {c: m.new_int_var(0, len(slots) - 1, f"slot_{c}") for c in courses}
day = {c: m.new_int_var(0, len(slots) // 2 - 1, f"day_{c}")
       for c in courses}
at = {(c, s): m.new_bool_var(f"{c}@{s}") for c in courses for s in slots}

for c in courses:
    m.add_division_equality(day[c], slot[c], 2)        # 2 sessions per day
    m.add_exactly_one(at[c, s] for s in slots)         # channel slot <-> at
    for s in slots:
        m.add(slot[c] == s).only_enforce_if(at[c, s])
    for s in unavailable.get(c, []):
        m.add(at[c, s] == 0)

for s in slots:                                        # seats per session
    m.add(sum(size[c] * at[c, s] for c in courses) <= seats)

penalty = []
for (a, b), n in shared.items():
    if n == 0:
        continue
    m.add(slot[a] != slot[b])                          # hard: no clash
    same = m.new_bool_var(f"same_{a}_{b}")             # soft: same day
    m.add(day[a] == day[b]).only_enforce_if(same)
    m.add(day[a] != day[b]).only_enforce_if(same.Not())
    penalty.append(n * same)                           # students affected
m.minimize(sum(penalty))


class Progress(cp_model.CpSolverSolutionCallback):
    def on_solution_callback(self):
        print(f"  {self.wall_time:5.2f} s   student-days with two exams: "
              f"{self.objective_value:.0f}")


solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
solver.parameters.num_workers = 8
status = solver.solve(m, Progress())
print("Status:", solver.status_name(status))
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise SystemExit("No timetable found")
names = ["Day 1 am", "Day 1 pm", "Day 2 am", "Day 2 pm",
         "Day 3 am", "Day 3 pm", "Day 4 am", "Day 4 pm"]
for s in slots:
    here = [c for c in courses if solver.value(slot[c]) == s]
    print(f"{names[s]}: {', '.join(here):<44} "
          f"{sum(size[c] for c in here):>3} seats")

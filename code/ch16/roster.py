"""Nurse rostering with CP-SAT: hard rules, requests and fairness."""
from ortools.sat.python import cp_model
from roster_data import (nurses, senior, shifts, days, weekend, need,
                         min_shifts, max_shifts, max_nights,
                         max_consecutive, day_off_requests, no_nights)

m = cp_model.CpModel()
x = {(n, d, s): m.new_bool_var(f"{n}_{d}_{s}")
     for n in nurses for d in days for s in shifts}
works = {(n, d): sum(x[n, d, s] for s in shifts)
         for n in nurses for d in days}

# ---- Hard rules ---------------------------------------------------
for n in nurses:
    for d in days:
        m.add_at_most_one(x[n, d, s] for s in shifts)    # one shift a day
    for d in days[:-1]:                                  # rest periods
        m.add_bool_or([x[n, d, "N"].Not(), x[n, d + 1, "M"].Not()])
        m.add_bool_or([x[n, d, "N"].Not(), x[n, d + 1, "E"].Not()])
        m.add_bool_or([x[n, d, "E"].Not(), x[n, d + 1, "M"].Not()])
    for d in days[:len(days) - max_consecutive]:     # max 5 days in a row
        m.add(sum(works[n, d + k] for k in range(max_consecutive + 1))
              <= max_consecutive)
    total = sum(works[n, d] for d in days)
    m.add(total >= min_shifts)
    m.add(total <= max_shifts)
    m.add(sum(x[n, d, "N"] for d in days)
          <= (0 if n in no_nights else max_nights))

for d in days:
    for s in shifts:
        m.add(sum(x[n, d, s] for n in nurses) >= need[d, s])
        m.add(sum(x[n, d, s] for n in senior) >= 1)      # a senior on duty

# ---- Soft rules ---------------------------------------------------
refused = sum(w * works[n, d] for (n, d), w in day_off_requests.items())

wk = {n: m.new_int_var(0, len(weekend), f"wk_{n}") for n in nurses}
for n in nurses:
    m.add(wk[n] == sum(works[n, d] for d in weekend))
most, least = m.new_int_var(0, 4, "most"), m.new_int_var(0, 4, "least")
m.add_max_equality(most, list(wk.values()))
m.add_min_equality(least, list(wk.values()))

m.minimize(10 * refused + 5 * (most - least))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
solver.parameters.num_workers = 8
status = solver.solve(m)
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise SystemExit(f"No roster found: {solver.status_name(status)}")
bound = ("" if status == cp_model.OPTIMAL     # time limit hit: show the
         else f" (bound {solver.best_objective_bound:.0f})")   # bound too
print(f"Status: {solver.status_name(status)}  "
      f"objective {solver.objective_value:.0f}{bound}")

print("day      " + "".join("SSMTWTF"[d % 7] for d in days)
      + "   shifts nights weekends")
for n in nurses:
    row = ""
    for d in days:
        s = [s for s in shifts if solver.value(x[n, d, s])]
        row += s[0] if s else ("-" if (n, d) in day_off_requests else ".")
    tag = "*" if n in senior else " "
    print(f"{n:<8}{tag}{row}   {sum(c != '.' and c != '-' for c in row):>6}"
          f" {row.count('N'):>6} {solver.value(wk[n]):>8}")
granted = sum(1 for (n, d) in day_off_requests
              if solver.value(works[n, d]) == 0)
print(f"Day-off requests granted: {granted} of {len(day_off_requests)}; "
      f"weekend shifts per nurse between {solver.value(least)} "
      f"and {solver.value(most)}")

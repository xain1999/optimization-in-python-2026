"""How many agents should start at each hour? A covering model (PuLP)."""
import pulp

# Agents needed in each hour of the day (call-centre forecast).
need = [4, 3, 3, 3, 3, 4, 7, 12, 18, 22, 24, 23,
        20, 21, 23, 22, 20, 18, 16, 14, 12, 10, 7, 5]
H = range(24)
shift_len = 8                         # an 8-hour shift starting at hour s
covers = {s: [(s + k) % 24 for k in range(shift_len)] for s in H}

model = pulp.LpProblem("Shift_Starts", pulp.LpMinimize)
start = model.add_variable_dict("start", H, lowBound=0, cat="Integer")
model += pulp.lpSum(start.values())                    # agents employed
for h in H:
    model += (pulp.lpSum(start[s] for s in H if h in covers[s]) >= need[h],
              f"cover_{h}")
model.solve(pulp.HiGHS(msg=False))

on_duty = [sum(start[s].value() for s in H if h in covers[s]) for h in H]
starts = [f"{s:02d}:00 x{start[s].value():.0f}" for s in H
          if start[s].value() > 0.5]
print("Shift starts: " + ", ".join(starts[:5]))
print("              " + ", ".join(starts[5:]))
print(f"Agents: {pulp.value(model.objective):.0f}   "
      f"(paid hours {8 * pulp.value(model.objective):.0f}, "
      f"required hours {sum(need)})")
print("hour  " + " ".join(f"{h:>2}" for h in H[:12]))
print("need  " + " ".join(f"{need[h]:>2}" for h in H[:12]))
print("duty  " + " ".join(f"{on_duty[h]:>2.0f}" for h in H[:12]))
print("hour  " + " ".join(f"{h:>2}" for h in H[12:]))
print("need  " + " ".join(f"{need[h]:>2}" for h in H[12:]))
print("duty  " + " ".join(f"{on_duty[h]:>2.0f}" for h in H[12:]))

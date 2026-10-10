"""The same truck-loading problem with the CP-SAT solver."""
from ortools.sat.python import cp_model
from pallet_data import pallets, trucks, max_pallets

model = cp_model.CpModel()

x = {(p, t): model.new_bool_var(f"x_{p}_{t}") for p in pallets for t in trucks}

for p in pallets:
    model.add_at_most_one(x[p, t] for t in trucks)

for t, cap in trucks.items():
    model.add(sum(pallets[p][0] * x[p, t] for p in pallets) <= cap)
    model.add(sum(x[p, t] for p in pallets) <= max_pallets)
    # Logical rule stated directly: no food together with chemicals.
    for p, (_, _, kp) in pallets.items():
        for q, (_, _, kq) in pallets.items():
            if kp == "food" and kq == "chemical":
                model.add_bool_or([x[p, t].Not(), x[q, t].Not()])

model.maximize(sum(pallets[p][1] * x[p, t] for p in pallets for t in trucks))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
solver.parameters.num_workers = 8                 # use 8 parallel workers
status = solver.solve(model)

print("Status:", solver.status_name(status))
for t in trucks:
    load = [p for p in pallets if solver.value(x[p, t])]
    kg = sum(pallets[p][0] for p in load)
    print(f"  {t}: {' '.join(load):<16} {kg:>5} kg")
print(f"Value shipped: ${solver.objective_value:,.0f}")
print(f"Solve time: {solver.wall_time:.2f} s")

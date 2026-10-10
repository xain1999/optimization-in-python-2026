"""Capacitated lot sizing: three juices on one bottling line (PuLP)."""
import pulp

products = ["orange", "apple", "mango"]
weeks = list(range(1, 9))
demand = {                                    # thousand bottles per week
    "orange": [30, 32, 35, 30, 28, 40, 45, 42],
    "apple":  [20, 18, 22, 25, 20, 18, 22, 24],
    "mango":  [10, 12, 8, 15, 14, 12, 18, 20],
}
rate = {"orange": 0.50, "apple": 0.45, "mango": 0.60}   # hours per unit
setup_time = {"orange": 4, "apple": 3, "mango": 6}      # hours per setup
setup_cost = {"orange": 900, "apple": 700, "mango": 1200}
hold_cost = {"orange": 12, "apple": 10, "mango": 15}    # $ per unit-week
hours = 60                                              # hours per week

model = pulp.LpProblem("Lot_Sizing", pulp.LpMinimize)
make = model.add_variable_dict("make", (products, weeks), lowBound=0)
stock = model.add_variable_dict("stock", (products, weeks), lowBound=0)
setup = model.add_variable_dict("setup", (products, weeks), cat="Binary")

model += pulp.lpSum(setup_cost[p] * setup[p, t] + hold_cost[p] * stock[p, t]
                    for p in products for t in weeks)

for p in products:
    for t in weeks:
        before = stock[p, t - 1] if t > 1 else 0          # no initial stock
        model += (before + make[p, t] == demand[p][t - 1] + stock[p, t],
                  f"balance_{p}_{t}")
        # Tight big-M: no more than the line allows or than is still needed
        remaining = sum(demand[p][t - 1:])
        big_m = min((hours - setup_time[p]) / rate[p], remaining)
        model += make[p, t] <= big_m * setup[p, t], f"setup_{p}_{t}"
for t in weeks:
    model += (pulp.lpSum(rate[p] * make[p, t] + setup_time[p] * setup[p, t]
                         for p in products) <= hours, f"hours_{t}")

result = model.solve(pulp.HiGHS(msg=False))
print("Status:", result.status_str)
print("week " + "".join(f"{t:>6}" for t in weeks))
for p in products:
    cells = [f"{make[p, t].value():6.0f}" if setup[p, t].value() > 0.5
             else f"{'.':>6}" for t in weeks]
    print(f"{p:<6}" + "".join(cells))
used = [sum(rate[p] * make[p, t].value()
            + setup_time[p] * setup[p, t].value() for p in products)
        for t in weeks]
print("hours " + "".join(f"{u:6.0f}" for u in used))
setups = sum(setup[p, t].value() for p in products for t in weeks)
print(f"Setups: {setups:.0f}, "
      f"total cost: ${pulp.value(model.objective):,.0f}")

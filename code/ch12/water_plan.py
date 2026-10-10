"""Seasonal production planning with overtime, stock and backlog (Pyomo)."""
import pyomo.environ as pyo
import water_data as d


def build_model(demand, initial_stock=d.initial_stock,
                final_stock=d.final_stock):
    m = pyo.ConcreteModel(name="Water_Plan")
    m.T = pyo.Set(initialize=list(demand), ordered=True)

    m.reg = pyo.Var(m.T, bounds=(0, d.regular_cap))      # regular shifts
    m.ot = pyo.Var(m.T, bounds=(0, d.overtime_cap))      # overtime
    m.stock = pyo.Var(m.T, bounds=(0, d.warehouse_cap))  # end of month
    m.back = pyo.Var(m.T, domain=pyo.NonNegativeReals)   # unmet, owed later

    @m.Objective()
    def cost(m):
        return sum(d.cost_regular * m.reg[t] + d.cost_overtime * m.ot[t]
                   + d.cost_hold * m.stock[t] + d.cost_backlog * m.back[t]
                   for t in m.T)

    @m.Constraint(m.T)
    def balance(m, t):              # what comes in = what goes out
        first = t == m.T.first()
        prev_stock = initial_stock if first else m.stock[m.T.prev(t)]
        prev_back = 0 if first else m.back[m.T.prev(t)]
        return (prev_stock + m.reg[t] + m.ot[t] + m.back[t]
                == demand[t] + prev_back + m.stock[t])

    last = m.T.last()
    m.end_stock = pyo.Constraint(expr=m.stock[last] >= final_stock)
    m.no_final_backlog = pyo.Constraint(expr=m.back[last] == 0)
    return m


if __name__ == "__main__":
    m = build_model(d.demand)
    pyo.SolverFactory("appsi_highs").solve(m)
    print(f"{'month':<5}{'demand':>8}{'regular':>9}{'overtime':>9}"
          f"{'stock':>7}{'backlog':>8}")
    rows = []
    for t in m.T:
        r = [pyo.value(v[t]) + 0.0 for v in (m.reg, m.ot, m.stock, m.back)]
        rows.append((t, d.demand[t], *r))
        print(f"{t:<5}{d.demand[t]:>8}" + "".join(
            f"{x:>{w}.0f}" for x, w in zip(r, (9, 9, 7, 8))))
    print(f"Total cost: ${1000 * pyo.value(m.cost):,.0f}")
    with open("output/water_plan.dat", "w") as f:      # data for the chart
        f.write("k month demand regular overtime stock backlog\n")
        for k, row in enumerate(rows, 1):
            cells = [x if isinstance(x, str) else str(round(x)) for x in row]
            f.write(f"{k} " + " ".join(cells) + "\n")

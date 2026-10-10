"""Rolling-horizon planning: how far ahead must we look?"""
import pyomo.environ as pyo
import water_data as d
from water_plan import build_model

months = list(d.demand)
solver = pyo.SolverFactory("appsi_highs")

def rolling_cost(horizon):
    """Each month, plan `horizon` months ahead; implement only month 1."""
    stock, back, total = d.initial_stock, 0.0, 0.0
    for k, t in enumerate(months):
        window = months[k:k + horizon]
        m = build_model({s: d.demand[s] for s in window},
                        initial_stock=stock, final_stock=0)
        m.balance[t].set_value(          # carry over last month's backlog
            stock + m.reg[t] + m.ot[t] + m.back[t]
            == d.demand[t] + back + m.stock[t])
        m.no_final_backlog.deactivate()  # a window may end with a backlog,
        end = m.T.last()                 # but it must be made up later:
        m.cost.expr = m.cost.expr + d.cost_overtime * m.back[end]
        solver.solve(m)
        reg, ot = pyo.value(m.reg[t]), pyo.value(m.ot[t])
        stock, back = pyo.value(m.stock[t]), pyo.value(m.back[t])
        total += (d.cost_regular * reg + d.cost_overtime * ot
                  + d.cost_hold * stock + d.cost_backlog * back)
    return 1000 * total

full = rolling_cost(12)
print(f"{'look-ahead':>10}{'annual cost':>14}{'extra':>11}")
for h in [1, 2, 3, 4, 6, 12]:
    c = rolling_cost(h)
    print(f"{h:>7} mo {c:>14,.0f}{c - full:>11,.0f}")

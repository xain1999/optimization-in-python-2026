"""Sahara Snacks (Chapter 5) as a Pyomo model."""
import sys
sys.path.append("../ch05")
import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import check_optimal_termination
from snacks_model import load_data


def build_model(d):
    m = pyo.ConcreteModel(name="Sahara_Snacks")

    # ---- Sets ---------------------------------------------------
    m.P = pyo.Set(initialize=d["P"], doc="products")
    m.K = pyo.Set(initialize=d["K"], doc="plants")
    m.A = pyo.Set(within=m.P * m.K, initialize=d["arcs"], doc="pairs")

    # ---- Parameters ---------------------------------------------
    m.price = pyo.Param(m.P, initialize=d["price"])
    m.min_dem = pyo.Param(m.P, initialize=d["min_dem"])
    m.max_dem = pyo.Param(m.P, initialize=d["max_dem"])
    m.hours_avail = pyo.Param(m.K, initialize=d["hours_avail"],
                              mutable=True)
    m.hours = pyo.Param(m.A, initialize=d["hours"])
    m.cost = pyo.Param(m.A, initialize=d["cost"])

    # ---- Variables ----------------------------------------------
    m.make = pyo.Var(m.A, domain=pyo.NonNegativeReals)

    # ---- Objective and constraints ------------------------------
    @m.Objective(sense=pyo.maximize)
    def profit(m):
        return sum((m.price[p] - m.cost[p, k]) * m.make[p, k]
                   for p, k in m.A)

    @m.Constraint(m.K)
    def capacity(m, k):
        used = sum(m.hours[p, kk] * m.make[p, kk]
                   for p, kk in m.A if kk == k)
        return used <= m.hours_avail[k]

    @m.Constraint(m.P)
    def demand(m, p):                   # ranged constraint: L <= . <= U
        total = sum(m.make[pp, k] for pp, k in m.A if pp == p)
        return pyo.inequality(m.min_dem[p], total, m.max_dem[p])

    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    return m


if __name__ == "__main__":
    m = build_model(load_data("../ch05/data"))
    solver = pyo.SolverFactory("appsi_highs")
    result = solver.solve(m, load_solutions=False)
    if not check_optimal_termination(result):
        cond = result.solver.termination_condition
        raise RuntimeError(f"Not optimal: {cond}")
    m.solutions.load_from(result)

    plan = pd.Series({a: pyo.value(m.make[a]) for a in m.A})
    print(plan.unstack(fill_value=0).reindex(index=list(m.P),
                                             columns=list(m.K)).round(1))
    print(f"Profit: {pyo.value(m.profit):,.0f}")
    print("Capacity duals:",
          {k: round(m.dual[m.capacity[k]], 2) for k in m.K})

"""Facility-location models for Mitidja Foods, built with Pyomo."""
import pyomo.environ as pyo
from pyomo.opt import check_optimal_termination


def build_model(d, capacitated=False, single_source=False, n_open=None):
    m = pyo.ConcreteModel(name="Distribution_Network")
    m.S = pyo.Set(initialize=list(d["fixed"]))       # candidate sites
    m.C = pyo.Set(initialize=list(d["demand"]))      # customer cities

    m.open = pyo.Var(m.S, domain=pyo.Binary)
    serve_domain = pyo.Binary if single_source else pyo.UnitInterval
    m.serve = pyo.Var(m.S, m.C, domain=serve_domain)  # share of c from s

    m.fixed_cost = pyo.Expression(
        expr=sum(d["fixed"][s] * m.open[s] for s in m.S))
    m.transport_cost = pyo.Expression(
        expr=sum(d["cost"][s, c] * m.serve[s, c] for s in m.S for c in m.C))
    m.total = pyo.Objective(expr=m.fixed_cost + m.transport_cost)

    @m.Constraint(m.C)
    def demand_met(m, c):
        return sum(m.serve[s, c] for s in m.S) == 1

    @m.Constraint(m.S, m.C)
    def only_if_open(m, s, c):                       # strong linking
        return m.serve[s, c] <= m.open[s]

    if capacitated:
        @m.Constraint(m.S)
        def capacity(m, s):
            return (sum(d["demand"][c] * m.serve[s, c] for c in m.C)
                    <= d["capacity"][s] * m.open[s])

    if n_open is not None:
        m.count = pyo.Constraint(expr=sum(m.open[s] for s in m.S) == n_open)
    return m


def solve(m, gap=0.0):
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = gap
    result = solver.solve(m, load_solutions=False)
    if not check_optimal_termination(result):
        raise RuntimeError(result.solver.termination_condition)
    m.solutions.load_from(result)
    opened = [s for s in m.S if pyo.value(m.open[s]) > 0.5]
    assign = {c: max(m.S, key=lambda s: pyo.value(m.serve[s, c]))
              for c in m.C}
    return opened, assign


def report(m, d, opened):
    print(f"Open: {', '.join(opened)}")
    fixed, transport = pyo.value(m.fixed_cost), pyo.value(m.transport_cost)
    print(f"Fixed ${fixed:,.0f} + delivery ${transport:,.0f} = "
          f"${fixed + transport:,.0f} per week")
    for s in opened:
        load = sum(d["demand"][c] * pyo.value(m.serve[s, c]) for c in m.C)
        print(f"  {s:<12} load {load:6.1f} t   capacity {d['capacity'][s]}")

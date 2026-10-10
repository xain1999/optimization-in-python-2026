"""Solve the same Pyomo model with different solvers."""
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.desks = pyo.Var(domain=pyo.NonNegativeReals)
m.shelves = pyo.Var(domain=pyo.NonNegativeReals)
m.profit = pyo.Objective(expr=70 * m.desks + 50 * m.shelves,
                         sense=pyo.maximize)
m.carpentry = pyo.Constraint(expr=4 * m.desks + 3 * m.shelves <= 240)
m.finishing = pyo.Constraint(expr=2 * m.desks + m.shelves <= 100)
m.demand = pyo.Constraint(expr=m.shelves <= 60)

for name in ["appsi_highs", "cbc", "glpk"]:
    solver = pyo.SolverFactory(name)
    if not solver.available(exception_flag=False):
        print(f"{name:<12} not available - skipped")
        continue
    solver.solve(m)
    print(f"{name:<12} profit = {pyo.value(m.profit):,.0f}")

"""Fixing variables and switching constraints off and on in Pyomo."""
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.desks = pyo.Var(domain=pyo.NonNegativeReals)
m.shelves = pyo.Var(domain=pyo.NonNegativeReals)
m.profit = pyo.Objective(expr=70 * m.desks + 50 * m.shelves,
                         sense=pyo.maximize)
m.carpentry = pyo.Constraint(expr=4 * m.desks + 3 * m.shelves <= 240)
m.finishing = pyo.Constraint(expr=2 * m.desks + m.shelves <= 100)
m.demand = pyo.Constraint(expr=m.shelves <= 60)
solver = pyo.SolverFactory("appsi_highs")

def show(label):
    solver.solve(m)
    print(f"{label:<28} desks={pyo.value(m.desks):5.1f} "
          f"shelves={pyo.value(m.shelves):5.1f} "
          f"profit={pyo.value(m.profit):6,.0f}")

show("base model")
m.desks.fix(10)                         # force 10 desks
show("desks fixed at 10")
m.desks.unfix()
m.finishing.deactivate()                # pretend finishing is unlimited
show("finishing deactivated")
m.finishing.activate()
m.contract = pyo.Constraint(expr=m.desks >= 35)   # add a new constraint
show("with contract desks >= 35")

import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.desks = pyo.Var(domain=pyo.NonNegativeReals)
m.shelves = pyo.Var(domain=pyo.NonNegativeReals)
m.profit = pyo.Objective(expr=70 * m.desks + 50 * m.shelves,
                         sense=pyo.maximize)
m.carpentry = pyo.Constraint(expr=4 * m.desks + 3 * m.shelves <= 240)
m.finishing = pyo.Constraint(expr=2 * m.desks + m.shelves <= 100)
m.demand = pyo.Constraint(expr=m.shelves <= 60)

m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)   # ask for duals
m.rc = pyo.Suffix(direction=pyo.Suffix.IMPORT)     # and reduced costs
pyo.SolverFactory("appsi_highs").solve(m)

for c in [m.carpentry, m.finishing, m.demand]:
    print(f"{c.name:<10} dual = {m.dual[c] + 0.0:6.2f}")
for v in [m.desks, m.shelves]:
    print(f"{v.name:<10} reduced cost = {m.rc[v] + 0.0:6.2f}")

import pyomo.environ as pyo

m = pyo.ConcreteModel(name="Atlas_Furniture")

m.desks   = pyo.Var(domain=pyo.NonNegativeReals)
m.shelves = pyo.Var(domain=pyo.NonNegativeReals)

m.profit = pyo.Objective(expr=70 * m.desks + 50 * m.shelves,
                         sense=pyo.maximize)
m.carpentry = pyo.Constraint(expr=4 * m.desks + 3 * m.shelves <= 240)
m.finishing = pyo.Constraint(expr=2 * m.desks + 1 * m.shelves <= 100)
m.demand    = pyo.Constraint(expr=m.shelves <= 60)

result = pyo.SolverFactory("appsi_highs").solve(m)

print("Status: ", result.solver.termination_condition)
print(f"Desks:   {pyo.value(m.desks):.1f}")
print(f"Shelves: {pyo.value(m.shelves):.1f}")
print(f"Profit:  {pyo.value(m.profit):,.0f}")

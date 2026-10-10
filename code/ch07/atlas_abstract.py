"""An abstract Pyomo model: structure first, data from a file later."""
import pyomo.environ as pyo

model = pyo.AbstractModel(name="Product_Mix")
model.P = pyo.Set()                          # products
model.R = pyo.Set()                          # resources
model.profit = pyo.Param(model.P)
model.cap = pyo.Param(model.R)
model.maxdem = pyo.Param(model.P)
model.use = pyo.Param(model.R, model.P, default=0)

model.x = pyo.Var(model.P, domain=pyo.NonNegativeReals)

def profit_rule(m):
    return sum(m.profit[p] * m.x[p] for p in m.P)
model.obj = pyo.Objective(rule=profit_rule, sense=pyo.maximize)

def capacity_rule(m, r):
    return sum(m.use[r, p] * m.x[p] for p in m.P) <= m.cap[r]
model.capacity = pyo.Constraint(model.R, rule=capacity_rule)

def demand_rule(m, p):
    return m.x[p] <= m.maxdem[p]
model.demand = pyo.Constraint(model.P, rule=demand_rule)

instance = model.create_instance("atlas.dat")   # combine structure + data
pyo.SolverFactory("appsi_highs").solve(instance)
for p in instance.P:
    print(f"{p:<6} {pyo.value(instance.x[p]):6.1f}")
print(f"Profit: {pyo.value(instance.obj):,.0f}")
instance.capacity.pprint()                       # inspect a component

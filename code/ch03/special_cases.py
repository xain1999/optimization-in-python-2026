"""Infeasible, unbounded and alternative-optima models in PuLP."""
import pulp

def report(title, model):
    result = model.solve(pulp.HiGHS(msg=False))
    print(f"{title:<22} status: {result.status_str}")
    if result.status_str == "Optimal":
        values = ", ".join(f"{v.name}={v.value():g}"
                           for v in model.variables())
        print(f"{'':<22} {values}, z={pulp.value(model.objective):g}")

# 1. Infeasible: the contract asks for more desks than finishing allows
m = pulp.LpProblem("Infeasible", pulp.LpMaximize)
x1 = m.add_variable("x1", lowBound=0)
x2 = m.add_variable("x2", lowBound=0)
m += 70 * x1 + 50 * x2
m += 2 * x1 + x2 <= 100, "Finishing"
m += x1 >= 60, "Desk_contract"
report("1. Infeasible", m)

# 2. Unbounded: the capacity constraints were forgotten
m = pulp.LpProblem("Unbounded", pulp.LpMaximize)
x1 = m.add_variable("x1", lowBound=0)
x2 = m.add_variable("x2", lowBound=0)
m += 70 * x1 + 50 * x2
m += x2 <= 60, "Shelf_demand"
report("2. Unbounded", m)

# 3. Alternative optima: profit parallel to the finishing constraint
m = pulp.LpProblem("Alternative", pulp.LpMaximize)
x1 = m.add_variable("x1", lowBound=0)
x2 = m.add_variable("x2", lowBound=0)
m += 100 * x1 + 50 * x2
m += 4 * x1 + 3 * x2 <= 240, "Carpentry"
m += 2 * x1 + x2 <= 100, "Finishing"
m += x2 <= 60, "Shelf_demand"
report("3. Alternative optima", m)

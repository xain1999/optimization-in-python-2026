"""Why rounding an LP solution is not enough."""
import pulp

def solve(integer):
    cat = "Integer" if integer else "Continuous"
    m = pulp.LpProblem("Rounding", pulp.LpMaximize)
    x1 = m.add_variable("x1", lowBound=0, cat=cat)
    x2 = m.add_variable("x2", lowBound=0, cat=cat)
    m += 21 * x1 + 11 * x2
    m += 7 * x1 + 4 * x2 <= 13
    m.solve(pulp.HiGHS(msg=False))
    return x1.value(), x2.value(), pulp.value(m.objective)

x1, x2, z = solve(integer=False)
print(f"LP relaxation:   x1 = {x1:.3f}, x2 = {x2:.3f}, z = {z:.2f}")
print(f"Rounded down:    x1 = 1.000, x2 = 0.000, z = {21 * 1 + 11 * 0:.2f}")
x1, x2, z = solve(integer=True)
print(f"Integer optimum: x1 = {x1:.3f}, x2 = {x2:.3f}, z = {z:.2f}")

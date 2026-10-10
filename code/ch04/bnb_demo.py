"""A tiny branch-and-bound, written out so every node is visible.

maximize 21 x1 + 11 x2   s.t.  7 x1 + 4 x2 <= 13,  x1, x2 >= 0 integer
"""
import math
import pulp

def solve_lp(bounds):
    """Solve the LP relaxation with extra bounds {var: (lo, hi)}."""
    m = pulp.LpProblem("node", pulp.LpMaximize)
    x = {j: m.add_variable(f"x{j}", lowBound=bounds[j][0],
                           upBound=bounds[j][1]) for j in (1, 2)}
    m += 21 * x[1] + 11 * x[2]
    m += 7 * x[1] + 4 * x[2] <= 13
    res = m.solve(pulp.HiGHS(msg=False))
    if res.status_str != "Optimal":
        return None, None
    return {j: x[j].value() for j in (1, 2)}, pulp.value(m.objective)

best_value, best_sol = -math.inf, None
stack = [("0", {1: (0, None), 2: (0, None)})]       # depth-first search
while stack:
    name, bounds = stack.pop()
    sol, z = solve_lp(bounds)
    if sol is None:
        print(f"node {name:<6} infeasible -> prune")
        continue
    desc = f"x1={sol[1]:.3f} x2={sol[2]:.3f} z={z:.2f}"
    if z <= best_value + 1e-9:
        print(f"node {name:<6} {desc}  bound <= incumbent -> prune")
        continue
    frac = [j for j in (1, 2) if abs(sol[j] - round(sol[j])) > 1e-6]
    if not frac:
        best_value, best_sol = z, sol
        print(f"node {name:<6} {desc}  integer -> new incumbent")
        continue
    j = frac[0]
    v = sol[j]
    lo, hi = bounds[j]
    print(f"node {name:<6} {desc}  branch on x{j}")
    down = dict(bounds); down[j] = (lo, math.floor(v))
    up = dict(bounds);   up[j] = (math.ceil(v), hi)
    stack.append((name + "R", up))
    stack.append((name + "L", down))

x1, x2 = best_sol[1], best_sol[2]
print(f"Optimal: x1={x1:.0f}, x2={x2:.0f}, z={best_value:.0f}")

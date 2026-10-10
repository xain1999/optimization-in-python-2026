"""The same TSP as a MILP (Miller-Tucker-Zemlin formulation) in PuLP."""
import pulp
from region_data import places, dist

n = len(places)
N = range(n)
arcs = [(i, j) for i in N for j in N if i != j]

m = pulp.LpProblem("TSP", pulp.LpMinimize)
x = m.add_variable_dict("x_%s_%s", arcs, cat="Binary")    # use arc i -> j
u = m.add_variable_dict("u", range(1, n), lowBound=1, upBound=n - 1)

m += pulp.lpSum(dist[i][j] * x[i, j] for i, j in arcs)
for k in N:
    m += pulp.lpSum(x[i, k] for i in N if i != k) == 1, f"enter_{k}"
    m += pulp.lpSum(x[k, j] for j in N if j != k) == 1, f"leave_{k}"
# MTZ: u is the position of each city in the tour; forbids subtours.
for i, j in arcs:
    if i != 0 and j != 0:
        m += u[i] - u[j] + (n - 1) * x[i, j] <= n - 2, f"mtz_{i}_{j}"

result = m.solve(pulp.HiGHS(msg=False))
print(f"Status: {result.status_str}, optimal tour length: "
      f"{pulp.value(m.objective):.0f} km")

"""Check that PuLP, OR-Tools, Pyomo and HiGHS are installed and work."""
import sys
from importlib.metadata import version, PackageNotFoundError

print(f"Python {sys.version.split()[0]}")
for pkg in ["pulp", "ortools", "pyomo", "highspy"]:
    try:
        print(f"  {pkg:<8} {version(pkg)}")
    except PackageNotFoundError:
        print(f"  {pkg:<8} NOT INSTALLED")

# A tiny test model:  maximize x + 2y  s.t.  x + y <= 4,  x, y >= 0
# The optimal value is 8 (x = 0, y = 4).

# --- PuLP ---------------------------------------------------------
import pulp
m = pulp.LpProblem("test", pulp.LpMaximize)
x = m.add_variable("x", lowBound=0)
y = m.add_variable("y", lowBound=0)
m += x + 2 * y
m += x + y <= 4
m.solve(pulp.HiGHS(msg=False))
print(f"PuLP     -> {pulp.value(m.objective):.1f}")
print("  PuLP solvers available:", pulp.listSolvers(onlyAvailable=True))

# --- OR-Tools -----------------------------------------------------
from ortools.linear_solver import pywraplp
s = pywraplp.Solver.CreateSolver("GLOP")
x = s.NumVar(0, s.infinity(), "x")
y = s.NumVar(0, s.infinity(), "y")
s.Add(x + y <= 4)
s.Maximize(x + 2 * y)
s.Solve()
print(f"OR-Tools -> {s.Objective().Value():.1f}")

# --- Pyomo --------------------------------------------------------
import pyomo.environ as pyo
p = pyo.ConcreteModel()
p.x = pyo.Var(domain=pyo.NonNegativeReals)
p.y = pyo.Var(domain=pyo.NonNegativeReals)
p.obj = pyo.Objective(expr=p.x + 2 * p.y, sense=pyo.maximize)
p.c = pyo.Constraint(expr=p.x + p.y <= 4)
pyo.SolverFactory("appsi_highs").solve(p)
print(f"Pyomo    -> {pyo.value(p.obj):.1f}")

print("All three libraries are working.")

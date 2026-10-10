"""Four PuLP pitfalls, each demonstrated in a few lines."""
import numpy as np
import pulp

def new_model():
    m = pulp.LpProblem("demo", pulp.LpMaximize)
    x = m.add_variable("x", lowBound=0)
    y = m.add_variable("y", lowBound=0)
    m += x + y
    return m, x, y

# 1. A repeated constraint name is accepted silently ...
m, x, y = new_model()
m += x <= 4, "limit"
m += y <= 3, "limit"                 # same name, different constraint
m.solve(pulp.HiGHS(msg=False))
print("1. solves:", x.value(), y.value())
try:                                 # ... but exporting the model fails
    m.writeMPS("demo.mps")
except pulp.PulpError as e:
    print("   export fails:", str(e).splitlines()[0])

# 2. NumPy integers cannot appear on the right-hand side
m, x, y = new_model()
cap = np.int64(10)                   # e.g. a value read with pandas
try:
    m += x + y <= cap
except TypeError as e:
    print("2. TypeError:", e)
m += x + y <= int(cap)               # convert to a Python number
print("   fixed with int():", m.constraints()[-1])

# 3. A comparison between plain numbers is just True or False
m, x, y = new_model()
m += x + y <= 10, "cap"
m.solve(pulp.HiGHS(msg=False))       # x.value() is now a plain number
m += x.value() <= 20                 # 'number <= 20' is True: ignored!
print("3. constraints after 'x.value() <= 20':", m.numConstraints())

# 4. A model with no lower bounds lets variables go negative
m = pulp.LpProblem("demo", pulp.LpMinimize)
z = m.add_variable("z")              # no lowBound: z is a free variable
m += 3 * z
m += z <= 100
print("4. status without lowBound:",
      m.solve(pulp.HiGHS(msg=False)).status_str)

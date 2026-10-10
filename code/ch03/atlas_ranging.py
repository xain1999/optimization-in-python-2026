"""Sensitivity ranges for the Atlas model using HiGHS directly."""
import highspy

h = highspy.Highs()
h.silent()

desks = h.addVariable(lb=0, name="desks")
shelves = h.addVariable(lb=0, name="shelves")
rows = {
    "Carpentry":    h.addConstr(4 * desks + 3 * shelves <= 240),
    "Finishing":    h.addConstr(2 * desks + 1 * shelves <= 100),
    "Shelf_demand": h.addConstr(shelves <= 60),
}
h.maximize(70 * desks + 50 * shelves)

status, rng = h.getRanging()
duals = h.getSolution().row_dual

print("Objective coefficient ranges (solution stays optimal):")
for j, name in enumerate(["desks", "shelves"]):
    print(f"  {name:<8} {rng.col_cost_dn.value_[j]:7.2f} to "
          f"{rng.col_cost_up.value_[j]:7.2f}")

print("Right-hand-side ranges (shadow price stays valid):")
for i, name in enumerate(rows):
    if abs(duals[i]) > 1e-9:                 # binding constraints only
        print(f"  {name:<10} price {duals[i]:5.2f}  rhs "
              f"{rng.row_bound_dn.value_[i]:6.1f} to "
              f"{rng.row_bound_up.value_[i]:6.1f}")

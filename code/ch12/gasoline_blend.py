"""Blending four refinery streams into two gasoline grades (PuLP)."""
import pulp

# component: (available m3/day, cost $/m3, octane, vapour pressure index)
comps = {
    "reformate":  (2600, 640, 98, 4.0),
    "FCC_naphtha": (3200, 590, 91, 6.5),
    "isomerate":  (1500, 620, 88, 11.5),
    "butane":     (900, 360, 93, 52.0),
}
# grade: (price $/m3, minimum octane, maximum vapour pressure index,
#         minimum daily volume m3)
grades = {"premium": (780, 95, 9.0, 2500), "regular": (720, 91, 10.0, 3000)}
C, G = list(comps), list(grades)

model = pulp.LpProblem("Gasoline_Blending", pulp.LpMaximize)
x = model.add_variable_dict("use", (C, G), lowBound=0)    # m3 of c in g
vol = {g: pulp.lpSum(x[c, g] for c in C) for g in G}       # grade volumes

model += pulp.lpSum(grades[g][0] * vol[g] for g in G) - pulp.lpSum(
    comps[c][1] * x[c, g] for c in C for g in G)

for c in C:
    model += pulp.lpSum(x[c, g] for g in G) <= comps[c][0], f"avail_{c}"
for g in G:
    price, octane, rvp, min_vol = grades[g]
    # Quality = volume-weighted average, written without division:
    #   sum(q_c * x_cg) / vol_g >= Q   <=>   sum((q_c - Q) * x_cg) >= 0
    model += (pulp.lpSum((comps[c][2] - octane) * x[c, g] for c in C) >= 0,
              f"octane_{g}")
    model += (pulp.lpSum((comps[c][3] - rvp) * x[c, g] for c in C) <= 0,
              f"rvp_{g}")
    model += vol[g] >= min_vol, f"volume_{g}"

model.solve(pulp.HiGHS(msg=False))
for g in G:
    v = pulp.value(vol[g])
    octane = sum(comps[c][2] * x[c, g].value() for c in C) / v
    rvp = sum(comps[c][3] * x[c, g].value() for c in C) / v
    mix = ", ".join(f"{c} {x[c, g].value() / v:.0%}" for c in C
                    if x[c, g].value() > 0.5)
    print(f"{g:<8} {v:6,.0f} m3   octane {octane:.1f}   RVP {rvp:.1f}")
    print(f"         {mix}")
print(f"Daily margin: ${pulp.value(model.objective):,.0f}")
print("Unused:", {c: round(model.get_constraint_by_name(f"avail_{c}").slack)
                  for c in C})

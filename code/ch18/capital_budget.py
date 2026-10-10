"""Multi-year capital budgeting for a regional water utility (PuLP)."""
import pulp

years = [1, 2, 3, 4]
# project: (net present value $M, spending per year $M, group)
projects = {
    "Desal_A":    (48, [30, 25, 10, 0], "desal"),      # two alternative
    "Desal_B":    (41, [18, 20, 12, 5], "desal"),      #   desalination plans
    "Dam_repair": (22, [8, 6, 0, 0], None),
    "Pipeline_N": (30, [5, 15, 12, 0], None),
    "Pipeline_S": (26, [4, 12, 14, 0], None),
    "Pumping_N":  (12, [0, 0, 6, 4], None),            # needs Pipeline_N
    "Leak_prog":  (19, [5, 5, 5, 5], None),
    "Meters":     (15, [6, 6, 0, 0], None),
    "Treatment":  (28, [0, 10, 15, 8], None),
    "Reuse":      (17, [0, 6, 8, 6], None),            # needs Treatment
    "Solar_pump": (9, [3, 3, 0, 0], None),
    "SCADA":      (11, [4, 4, 2, 0], None),
}
budget = {1: 60, 2: 70, 3: 55, 4: 30}              # $M available per year
carry_rate = 0.03                         # interest on unspent funds
P = list(projects)

m = pulp.LpProblem("Capital_Budgeting", pulp.LpMaximize)
x = m.add_variable_dict("do", P, cat="Binary")
carry = m.add_variable_dict("carry", years, lowBound=0)   # unspent, $M

m += pulp.lpSum(projects[p][0] * x[p] for p in P)
for t in years:                         # spending + carry-over <= available
    previous = (1 + carry_rate) * carry[t - 1] if t > 1 else 0
    m += (pulp.lpSum(projects[p][1][t - 1] * x[p] for p in P) + carry[t]
          == budget[t] + previous, f"budget_{t}")
m += x["Desal_A"] + x["Desal_B"] <= 1, "one_desal_plant"
m += x["Pumping_N"] <= x["Pipeline_N"], "pumping_needs_pipeline"
m += x["Reuse"] <= x["Treatment"], "reuse_needs_treatment"

m.solve(pulp.HiGHS(msg=False))
chosen = [p for p in P if x[p].value() > 0.5]
print(f"Selected ({len(chosen)}): {', '.join(chosen[:6])}")
print(f"              {', '.join(chosen[6:])}")
print(f"Total NPV: ${pulp.value(m.objective):.0f}M")
for t in years:
    spent = sum(projects[p][1][t - 1] for p in chosen)
    print(f"  Year {t}: spend {spent:5.1f}  budget {budget[t]:3}  "
          f"carried forward {carry[t].value():5.2f}")

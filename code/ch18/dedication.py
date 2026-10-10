"""Cash-flow matching: the cheapest bond portfolio that pays a pension
fund's liabilities for the next six years (PuLP)."""
import pulp

years = range(1, 7)
liability = {1: 12, 2: 14, 3: 15, 4: 16, 5: 18, 6: 20}     # $M per year
# bond: (price per 100 face, annual coupon per 100, maturity in years)
bonds = {
    "B1": (99.2, 2.5, 1), "B2": (98.6, 3.0, 2), "B3": (100.4, 4.5, 2),
    "B4": (97.1, 3.5, 3), "B5": (101.5, 5.5, 4), "B6": (95.0, 3.0, 5),
    "B7": (103.0, 6.0, 5), "B8": (96.4, 4.0, 6), "B9": (92.0, 2.5, 6),
}
reinvest = 0.02                      # surplus cash earns 2% a year

m = pulp.LpProblem("Dedication", pulp.LpMinimize)
units = m.add_variable_dict("units", bonds, lowBound=0)  # face value / 100
surplus = m.add_variable_dict("surplus", years, lowBound=0)
start_cash = m.add_variable("start_cash", lowBound=0)

m += start_cash + pulp.lpSum(bonds[b][0] * units[b] for b in bonds) / 1e6
for t in years:
    paid = pulp.lpSum(                # coupons, plus face value at maturity
        (bonds[b][1] + (100 if bonds[b][2] == t else 0)) * units[b]
        for b in bonds if bonds[b][2] >= t) / 1e6
    before = start_cash if t == 1 else surplus[t - 1]
    m += ((1 + reinvest) * before + paid - surplus[t] == liability[t],
          f"year_{t}")

m.solve(pulp.HiGHS(msg=False))
print(f"Cost today: ${pulp.value(m.objective):.2f}M "
      f"for ${sum(liability.values())}M of liabilities")
for b in bonds:
    if units[b].value() > 1e-6:
        print(f"  buy {b}: face ${units[b].value() * 100 / 1e6:6.2f}M "
              f"(price {bonds[b][0]}, coupon {bonds[b][1]}%, "
              f"matures year {bonds[b][2]})")
print("Implied value today of $1 paid in year t:")
print("  " + "  ".join(
    f"t={t}: {abs(m.get_constraint_by_name(f'year_{t}').pi):.3f}"
    for t in years))

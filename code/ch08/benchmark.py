"""Build and solve the farm model at several sizes in all three libraries."""
from farm_data import generate
import farm_pulp
import farm_ortools
import farm_pyomo

libraries = [("PuLP + HiGHS", farm_pulp.solve),
             ("OR-Tools + SCIP", farm_ortools.solve),
             ("Pyomo + HiGHS", farm_pyomo.solve)]

print(f"{'fields':>6}  {'library':<16}{'objective':>12}"
      f"{'build':>8}{'solve':>8}{'total':>8}   (seconds)")
for n in [100, 400, 1600]:
    data = generate(n, seed=1)
    for name, solve in libraries:
        obj, plan, t_build, t_solve = solve(data, time_limit=120)
        # Independent check of the diversity rule on the returned plan
        assert len(set(plan.values())) >= data["min_crops"], name
        print(f"{n:>6}  {name:<16}{obj:>12,.0f}"
              f"{t_build:>8.2f}{t_solve:>8.2f}{t_build + t_solve:>8.2f}")

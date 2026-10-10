"""Excel in, Excel out: Sahara Snacks with a planner's workbook."""
import sys
from pathlib import Path
sys.path.append("../ch05")
import pandas as pd
import pulp
from snacks_model import build_model

# The planner's workbook has three sheets. For the demonstration it is
# created from the CSV files, but only if it does not exist yet, so your
# own edits to snacks_input.xlsx are kept. Delete it to start over.
INPUT = Path("snacks_input.xlsx")
COLUMNS = {"products": ["product", "price", "min_demand", "max_demand"],
           "plants": ["plant", "hours"],
           "routes": ["product", "plant", "hours_per_carton",
                      "cost_per_carton"]}
if not INPUT.exists():
    with pd.ExcelWriter(INPUT) as xl:
        for sheet in COLUMNS:
            pd.read_csv(f"../ch05/data/{sheet}.csv").to_excel(
                xl, sheet_name=sheet, index=False)

# ---- Read and check ----------------------------------------------------
sheets = pd.read_excel(INPUT, sheet_name=None)       # all sheets at once
for sheet, cols in COLUMNS.items():
    if sheet not in sheets:
        sys.exit(f"{INPUT}: sheet '{sheet}' is missing")
    missing = [c for c in cols if c not in sheets[sheet].columns]
    if missing or sheets[sheet][cols].isna().any().any():
        sys.exit(f"{INPUT}, sheet '{sheet}': missing columns {missing} "
                 f"or empty cells")
products = sheets["products"].set_index("product")
plants = sheets["plants"].set_index("plant")
routes = sheets["routes"].set_index(["product", "plant"])
data = {
    "P": list(products.index), "K": list(plants.index),
    "arcs": list(routes.index),
    "price": products["price"].to_dict(),
    "min_dem": products["min_demand"].to_dict(),
    "max_dem": products["max_demand"].to_dict(),
    "hours_avail": plants["hours"].to_dict(),
    "hours": routes["hours_per_carton"].to_dict(),
    "cost": routes["cost_per_carton"].to_dict(),
}

# ---- Solve -------------------------------------------------------------
model, make = build_model(data)
result = model.solve(pulp.HiGHS(msg=False))
if not result.has_solution:          # never report an unusable result
    sys.exit(f"No plan to report: {result.status_str}")

# ---- Write -------------------------------------------------------------
plan = pd.DataFrame([(p, k, make[p, k].value()) for p, k in data["arcs"]],
                    columns=["product", "plant", "cartons"])
use = plan.merge(routes.reset_index(), on=["product", "plant"])
use["hours"] = use["cartons"] * use["hours_per_carton"]
plant_use = use.groupby("plant")["hours"].sum().to_frame("hours used")
plant_use["available"] = plants["hours"]
plant_use["utilization"] = plant_use["hours used"] / plant_use["available"]
summary = pd.DataFrame({"value": [result.status_str,
                                  round(pulp.value(model.objective), 2),
                                  plan["cartons"].sum().round(1)]},
                       index=["status", "profit ($)", "cartons made"])

with pd.ExcelWriter("snacks_results.xlsx") as xl:
    summary.to_excel(xl, sheet_name="Summary")
    plan.pivot(index="product", columns="plant", values="cartons") \
        .fillna(0).round(1).to_excel(xl, sheet_name="Plan")
    plant_use.round(3).to_excel(xl, sheet_name="Plants")

print("Wrote snacks_results.xlsx with sheets:",
      pd.ExcelFile("snacks_results.xlsx").sheet_names)
print(summary.to_string())
print(plant_use.round(2).to_string())

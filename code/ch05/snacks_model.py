"""Sahara Snacks model, organized as reusable functions."""
import pandas as pd
import pulp


def load_data(folder="data"):
    """Read the CSV files and return plain Python dictionaries."""
    products = pd.read_csv(f"{folder}/products.csv", index_col="product")
    plants = pd.read_csv(f"{folder}/plants.csv", index_col="plant")
    routes = pd.read_csv(f"{folder}/routes.csv",
                         index_col=["product", "plant"])
    return {
        "P": list(products.index),
        "K": list(plants.index),
        "arcs": list(routes.index),
        "price": products["price"].to_dict(),
        "min_dem": products["min_demand"].to_dict(),
        "max_dem": products["max_demand"].to_dict(),
        "hours_avail": plants["hours"].to_dict(),
        "hours": routes["hours_per_carton"].to_dict(),
        "cost": routes["cost_per_carton"].to_dict(),
    }


def build_model(d):
    """Build the production-planning LP from the data dictionary d."""
    arcs = d["arcs"]
    model = pulp.LpProblem("Sahara_Snacks", pulp.LpMaximize)
    make = model.add_variable_dict("make_%s_%s", arcs, lowBound=0)

    model += pulp.lpSum((d["price"][p] - d["cost"][p, k]) * make[p, k]
                        for p, k in arcs), "Profit"
    for k in d["K"]:
        model += (pulp.lpSum(d["hours"][p, kk] * make[p, kk]
                             for p, kk in arcs if kk == k)
                  <= d["hours_avail"][k]), f"hours_{k}"
    for p in d["P"]:
        total = pulp.lpSum(make[pp, k] for pp, k in arcs if pp == p)
        model += total >= d["min_dem"][p], f"min_{p}"
        model += total <= d["max_dem"][p], f"max_{p}"
    return model, make


def plan_table(d, make):
    """Return the production plan as a products x plants DataFrame."""
    plan = pd.Series({a: make[a].value() for a in d["arcs"]})
    return (plan.unstack(fill_value=0)
                .reindex(index=d["P"], columns=d["K"], fill_value=0)
                .round(1))

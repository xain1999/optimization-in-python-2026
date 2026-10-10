"""Least-cost animal feed: a minimization LP with >=, <= and =."""
import pulp

ingredients = ["corn", "soymeal", "fishmeal", "bran", "oil", "limestone"]
cost = {"corn": 0.28, "soymeal": 0.52, "fishmeal": 1.10,   # $ per kg
        "bran": 0.18, "oil": 1.25, "limestone": 0.06}

# Nutrient content as a fraction of weight
content = {
    "protein": {"corn": 0.09, "soymeal": 0.46, "fishmeal": 0.62,
                "bran": 0.15, "oil": 0.00, "limestone": 0.00},
    "fat":     {"corn": 0.04, "soymeal": 0.02, "fishmeal": 0.09,
                "bran": 0.04, "oil": 0.99, "limestone": 0.00},
    "fibre":   {"corn": 0.02, "soymeal": 0.06, "fishmeal": 0.01,
                "bran": 0.11, "oil": 0.00, "limestone": 0.00},
    "calcium": {"corn": 0.0003, "soymeal": 0.003, "fishmeal": 0.05,
                "bran": 0.001, "oil": 0.00, "limestone": 0.38},
}
batch = 1000                                     # kg of feed per batch
min_frac = {"protein": 0.20, "fat": 0.035, "calcium": 0.010}
max_frac = {"fibre": 0.05}

model = pulp.LpProblem("Feed_Mix", pulp.LpMinimize)
kg = model.add_variable_dict("kg", ingredients, lowBound=0)

model += pulp.lpSum(cost[i] * kg[i] for i in ingredients), "Cost"
model += pulp.lpSum(kg[i] for i in ingredients) == batch, "Batch_size"
for n, f in min_frac.items():
    model += (pulp.lpSum(content[n][i] * kg[i] for i in ingredients)
              >= f * batch), f"min_{n}"
for n, f in max_frac.items():
    model += (pulp.lpSum(content[n][i] * kg[i] for i in ingredients)
              <= f * batch), f"max_{n}"

result = model.solve(pulp.HiGHS(msg=False))

print("Status:", result.status_str)
for i in ingredients:
    print(f"  {i:<10} {kg[i].value():8.1f} kg   "
          f"reduced cost {kg[i].dj + 0.0:7.4f}")
print(f"Cost per batch: ${pulp.value(model.objective):,.2f}")
print("Constraint            slack     dual")
for c in model.constraints():
    print(f"  {c.name:<16} {c.slack + 0.0:9.2f} {c.pi + 0.0:9.4f}")

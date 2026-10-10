"""Data for the Tassili Cement examples (weekly, in tonnes)."""
import sys
sys.path.append("../common")
from geo import road_km

plants = {"Chlef": 3000, "Batna": 2400, "Skikda": 1800}       # capacity
prod_cost = {"Chlef": 38.0, "Batna": 35.0, "Skikda": 41.0}    # $ per t
demand = {"Algiers": 1500, "Oran": 1100, "Constantine": 900,
          "Setif": 700, "Tlemcen": 500, "Djelfa": 400,
          "Annaba": 600, "Tiaret": 500}
rate = 0.06                                     # $ per tonne-km by road

ship_cost = {(p, c): round(rate * road_km(p, c), 2)
             for p in plants for c in demand}

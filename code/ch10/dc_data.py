"""Data for the Mitidja Foods distribution-network examples (weekly)."""
import sys
sys.path.append("../common")
from geo import CITIES, road_km

# Weekly demand in tonnes, roughly proportional to the population served.
demand = {
    "Algiers": 170, "Oran": 80, "Constantine": 47, "Annaba": 32,
    "Blida": 50, "Batna": 56, "Djelfa": 58, "Setif": 75,
    "Sidi Bel Abbes": 30, "Biskra": 37, "Tebessa": 33, "Tiaret": 43,
    "Bejaia": 46, "Tlemcen": 48, "Bechar": 14, "Mostaganem": 37,
    "Bordj Bou Arreridj": 32, "Chlef": 50, "Skikda": 45, "Tizi Ouzou": 57,
    "Medea": 41, "Ouargla": 28, "Ghardaia": 18, "Laghouat": 23,
    "Msila": 50, "Jijel": 32, "Relizane": 37, "Saida": 17,
    "Mascara": 39, "El Oued": 33,
}
# Candidate distribution centres: weekly fixed cost ($) and capacity (t).
sites = {
    "Algiers":     (7000, 400), "Blida":    (5500, 400),
    "Oran":        (6000, 320), "Chlef":    (4500, 300),
    "Tlemcen":     (4200, 250), "Setif":    (5000, 340),
    "Constantine": (5800, 350), "Batna":    (4500, 300),
    "Biskra":      (4000, 250), "Ghardaia": (3800, 200),
}
fixed = {s: f for s, (f, _) in sites.items()}
capacity = {s: c for s, (_, c) in sites.items()}
rate = 0.20                        # $ per tonne-km (refrigerated trucks)
cost = {(s, c): round(rate * road_km(s, c) * demand[c], 2)
        for s in sites for c in demand}   # serving ALL of city c from s
coords = {c: CITIES[c] for c in demand}

"""Data for the farm-planning model of Chapter 8.

small() returns the 12-field case study; generate(n) builds larger
random instances with the same structure for benchmarking.
"""
import random

MONTHS = ["Mar", "Apr", "May", "Jun", "Jul", "Aug"]

# crop: yield (t/ha), price ($/t), cost ($/ha), market limit (ha)
CROPS = {
    "wheat":    (3.2, 280, 420, 60),
    "barley":   (2.8, 240, 360, 40),
    "potato":   (28.0, 120, 2600, 25),
    "tomato":   (45.0, 90, 3400, 15),
    "chickpea": (1.6, 900, 520, 30),
    "olive":    (4.0, 650, 1300, 20),
}
# water need per ha by month (thousand m3), and labour (person-days per ha)
WATER = {
    "wheat":    [0.6, 0.8, 0.4, 0.0, 0.0, 0.0],
    "barley":   [0.5, 0.6, 0.3, 0.0, 0.0, 0.0],
    "potato":   [0.4, 0.9, 1.2, 1.3, 0.6, 0.0],
    "tomato":   [0.0, 0.5, 1.1, 1.6, 1.8, 1.2],
    "chickpea": [0.3, 0.4, 0.3, 0.1, 0.0, 0.0],
    "olive":    [0.2, 0.3, 0.5, 0.7, 0.8, 0.7],
}
LABOUR = {
    "wheat":    [0.5, 0.2, 0.2, 1.0, 0.3, 0.0],
    "barley":   [0.5, 0.2, 0.2, 0.9, 0.0, 0.0],
    "potato":   [3.0, 1.5, 1.5, 2.0, 4.0, 0.0],
    "tomato":   [1.0, 4.0, 3.0, 4.0, 6.0, 6.0],
    "chickpea": [0.8, 0.3, 0.3, 1.5, 0.5, 0.0],
    "olive":    [0.5, 0.5, 0.3, 0.3, 0.3, 0.3],
}


def _build(areas, quality, water_cap, labour_cap, scale):
    fields = list(areas)
    crops = list(CROPS)
    revenue = {(f, c): round(areas[f] * (quality[f] * CROPS[c][0] * CROPS[c][1]
                                         - CROPS[c][2]))
               for f in fields for c in crops}
    return {
        "fields": fields, "crops": crops, "months": MONTHS,
        "area": areas, "revenue": revenue,
        "water": {(c, m): WATER[c][i] for c in crops
                  for i, m in enumerate(MONTHS)},
        "labour": {(c, m): LABOUR[c][i] for c in crops
                   for i, m in enumerate(MONTHS)},
        "water_cap": {m: water_cap[i] * scale for i, m in enumerate(MONTHS)},
        "labour_cap": {m: labour_cap[i] * scale for i, m in enumerate(MONTHS)},
        "market": {c: CROPS[c][3] * scale for c in crops},
        "min_crops": 3,
    }


def small():
    areas = {"F01": 12, "F02": 8, "F03": 15, "F04": 6, "F05": 10, "F06": 9,
             "F07": 14, "F08": 7, "F09": 11, "F10": 5, "F11": 13, "F12": 10}
    quality = {"F01": 1.0, "F02": 0.9, "F03": 1.1, "F04": 0.8, "F05": 1.0,
               "F06": 1.2, "F07": 0.9, "F08": 1.0, "F09": 1.1, "F10": 0.7,
               "F11": 1.0, "F12": 0.95}
    return _build(areas, quality,
                  water_cap=[60, 80, 85, 75, 60, 40],
                  labour_cap=[220, 260, 220, 300, 300, 200], scale=1)


def generate(n_fields, seed=1):
    rng = random.Random(seed)
    areas = {f"F{i:04d}": rng.randint(4, 16) for i in range(n_fields)}
    quality = {f: round(rng.uniform(0.7, 1.2), 2) for f in areas}
    scale = n_fields / 12
    return _build(areas, quality,
                  water_cap=[60, 80, 85, 75, 60, 40],
                  labour_cap=[220, 260, 220, 300, 300, 200], scale=scale)

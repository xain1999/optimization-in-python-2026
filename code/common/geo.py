"""Approximate coordinates of Algerian cities and a road-distance estimate.

Coordinates are rounded city-centre values (latitude, longitude) for
teaching purposes. Road distance is estimated as the great-circle distance
multiplied by a detour factor of 1.25, a common rule of thumb.
"""
from math import asin, cos, radians, sin, sqrt

CITIES = {
    "Algiers": (36.75, 3.06),     "Oran": (35.70, -0.63),
    "Constantine": (36.37, 6.61), "Annaba": (36.90, 7.77),
    "Blida": (36.47, 2.83),       "Batna": (35.56, 6.17),
    "Djelfa": (34.67, 3.26),      "Setif": (36.19, 5.41),
    "Sidi Bel Abbes": (35.19, -0.63), "Biskra": (34.85, 5.73),
    "Tebessa": (35.40, 8.12),     "Tiaret": (35.37, 1.32),
    "Bejaia": (36.75, 5.08),      "Tlemcen": (34.88, -1.32),
    "Bechar": (31.62, -2.22),     "Mostaganem": (35.93, 0.09),
    "Bordj Bou Arreridj": (36.07, 4.76), "Chlef": (36.17, 1.33),
    "Skikda": (36.88, 6.91),      "Tizi Ouzou": (36.71, 4.05),
    "Medea": (36.26, 2.75),       "Ouargla": (31.95, 5.32),
    "Ghardaia": (32.49, 3.67),    "Laghouat": (33.80, 2.87),
    "Msila": (35.70, 4.54),       "Jijel": (36.82, 5.77),
    "Relizane": (35.74, 0.56),    "Saida": (34.83, 0.15),
    "Mascara": (35.40, 0.14),     "El Oued": (33.37, 6.86),
}


def great_circle_km(a, b):
    """Great-circle distance in km between two (lat, lon) points."""
    (lat1, lon1), (lat2, lon2) = a, b
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = p2 - p1, radians(lon2 - lon1)
    h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def road_km(city1, city2, detour=1.25):
    """Estimated road distance in km between two named cities."""
    return round(detour * great_circle_km(CITIES[city1], CITIES[city2]))

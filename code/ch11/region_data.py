"""Daily deliveries from the Blida distribution centre (Chapter 11)."""
import sys
sys.path.append("../common")
from geo import CITIES, road_km

depot = "Blida"
customers = ["Algiers", "Tizi Ouzou", "Medea", "Chlef", "Bejaia",
             "Bordj Bou Arreridj", "Msila", "Djelfa", "Tiaret", "Relizane",
             "Mostaganem", "Laghouat", "Setif", "Jijel", "Mascara"]
places = [depot] + customers                    # node 0 is the depot

# Integer road distances (km): the routing library needs integers.
dist = [[road_km(a, b) for b in places] for a in places]

# Daily demand (tonnes) and delivery time windows (hours after midnight).
demand = [0, 9, 4, 3, 3, 4, 2, 3, 3, 2, 2, 2, 1, 3, 2, 2]
windows = [(5, 21),                             # depot opening hours
           (6, 10), (7, 13), (6, 12), (8, 15), (8, 16), (9, 17), (9, 17),
           (8, 16), (10, 18), (10, 18), (9, 17), (10, 18), (10, 18),
           (9, 17), (10, 18)]
service_min = 30                                # minutes unloading per stop
speed_kmh = 70
coords = [CITIES[p] for p in places]

"""Capacitated vehicle routing: four 12-tonne trucks from Blida."""
from region_data import places, dist, demand
from vrp_common import create, add_capacity, solve, routes

trucks = [12, 12, 12, 12]                         # capacity in tonnes
manager, routing = create(len(places), len(trucks), dist)
add_capacity(manager, routing, demand, trucks)
solution = solve(routing)

for v, r in enumerate(routes(manager, routing, solution)):
    km = sum(dist[a][b] for a, b in zip(r, r[1:]))
    load = sum(demand[i] for i in r)
    stops = " - ".join(places[i] for i in r[1:-1]) or "(unused)"
    print(f"Truck {v + 1}: {km:4} km, {load:2} t: {stops}")
print(f"Total distance: {solution.ObjectiveValue()} km")

"""Only four trucks today: which deliveries should be postponed?"""
from region_data import (places, dist, demand, windows, service_min,
                         speed_kmh)
from vrp_common import create, add_capacity, add_time, solve, routes

trucks = [12] * 4
manager, routing = create(len(places), len(trucks), dist)
add_capacity(manager, routing, demand, trucks)
add_time(manager, routing, dist, windows, service_min, speed_kmh,
         max_shift_min=12 * 60)

# Each customer may be skipped at a penalty of 150 km-equivalents per tonne.
for node in range(1, len(places)):
    routing.AddDisjunction([manager.NodeToIndex(node)], 150 * demand[node])

solution = solve(routing, seconds=10)
served = set()
for v, r in enumerate(routes(manager, routing, solution)):
    served.update(r)
    km = sum(dist[a][b] for a, b in zip(r, r[1:]))
    print(f"Truck {v + 1}: {km:4} km  "
          + " - ".join(places[i] for i in r[1:-1]))
dropped = [places[i] for i in range(1, len(places)) if i not in served]
print("Postponed:", ", ".join(dropped),
      f"({sum(demand[places.index(p)] for p in dropped)} t)")

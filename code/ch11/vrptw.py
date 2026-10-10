"""Vehicle routing with time windows and driver shifts."""
from region_data import (places, dist, demand, windows, service_min,
                         speed_kmh)
from vrp_common import create, add_capacity, add_time, solve, routes

trucks = [12] * 6                                 # up to six trucks
manager, routing = create(len(places), len(trucks), dist)
add_capacity(manager, routing, demand, trucks)
time = add_time(manager, routing, dist, windows, service_min, speed_kmh,
                max_shift_min=12 * 60)            # 12-hour driver shift
routing.SetFixedCostOfAllVehicles(400)        # each truck used "costs" 400
solution = solve(routing, seconds=10)
if solution is None:
    raise SystemExit("No feasible plan found")

def hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

used, total_km = 0, 0
for v, r in enumerate(routes(manager, routing, solution)):
    if len(r) == 2:
        continue
    used += 1
    km = sum(dist[a][b] for a, b in zip(r, r[1:]))   # from the route itself
    total_km += km
    print(f"Truck {v + 1} ({km} km, {sum(demand[i] for i in r)} t)")
    index = routing.Start(v)
    for node in r[:-1]:
        t = solution.Min(time.CumulVar(index))
        print(f"   {hhmm(t)}  {places[node]}")
        index = solution.Value(routing.NextVar(index))
    print(f"   {hhmm(solution.Min(time.CumulVar(index)))}  back at depot")
print(f"Trucks used: {used}, total distance: {total_km} km")

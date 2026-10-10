"""One truck visits every customer: a TSP with OR-Tools routing."""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from region_data import places, dist

n = len(places)
manager = pywrapcp.RoutingIndexManager(n, 1, 0)   # nodes, vehicles, depot
routing = pywrapcp.RoutingModel(manager)

def distance(from_index, to_index):               # called by the solver
    i = manager.IndexToNode(from_index)
    j = manager.IndexToNode(to_index)
    return dist[i][j]

transit = routing.RegisterTransitCallback(distance)
routing.SetArcCostEvaluatorOfAllVehicles(transit)

params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
params.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
params.time_limit.FromSeconds(5)

solution = routing.SolveWithParameters(params)
if solution is None:                              # nothing found in time
    raise SystemExit(f"No route found (status {routing.status()})")

index, route = routing.Start(0), []
while not routing.IsEnd(index):
    route.append(places[manager.IndexToNode(index)])
    index = solution.Value(routing.NextVar(index))
route.append(places[0])
for k in range(0, len(route), 6):                 # print 6 stops per line
    print(" -> ".join(route[k:k + 6]))
print(f"Total distance: {solution.ObjectiveValue()} km")

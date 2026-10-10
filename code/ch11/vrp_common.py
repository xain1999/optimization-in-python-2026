"""Helpers shared by the vehicle-routing examples of Chapter 11."""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def create(n_nodes, n_vehicles, dist):
    """Manager and routing model with distance as the arc cost."""
    manager = pywrapcp.RoutingIndexManager(n_nodes, n_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance(a, b):
        return dist[manager.IndexToNode(a)][manager.IndexToNode(b)]

    transit = routing.RegisterTransitCallback(distance)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)
    return manager, routing


def add_capacity(manager, routing, demand, capacities):
    """Vehicle load may never exceed its capacity."""
    def load(a):
        return demand[manager.IndexToNode(a)]

    cb = routing.RegisterUnaryTransitCallback(load)
    routing.AddDimensionWithVehicleCapacity(
        cb, 0, capacities, True, "Load")   # slack 0, start empty


def solve(routing, seconds=5):
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    params.time_limit.FromSeconds(seconds)
    return routing.SolveWithParameters(params)


def routes(manager, routing, solution):
    """List of routes, one per vehicle, as lists of node numbers."""
    result = []
    for v in range(routing.vehicles()):
        index, route = routing.Start(v), []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        result.append(route + [0])
    return result


def add_time(manager, routing, dist, windows, service_min, speed_kmh,
             max_shift_min):
    """Travel + service time, delivery windows and a maximum shift."""
    def travel(a, b):
        i, j = manager.IndexToNode(a), manager.IndexToNode(b)
        drive = round(60 * dist[i][j] / speed_kmh)
        return drive + (service_min if i != 0 else 0)   # unload at i

    cb = routing.RegisterTransitCallback(travel)
    routing.AddDimension(cb, 180, 24 * 60, False, "Time")  # wait <= 3 h
    time = routing.GetDimensionOrDie("Time")
    for node, (start, end) in enumerate(windows):
        if node > 0:                                     # customer windows
            index = manager.NodeToIndex(node)
            time.CumulVar(index).SetRange(60 * start, 60 * end)
    open_, close = 60 * windows[0][0], 60 * windows[0][1]
    for v in range(routing.vehicles()):                 # depot hours, shift
        for index in (routing.Start(v), routing.End(v)):
            time.CumulVar(index).SetRange(open_, close)
            routing.AddVariableMinimizedByFinalizer(time.CumulVar(index))
        time.SetSpanUpperBoundForVehicle(max_shift_min, v)
    return time

"""24-hour unit commitment and dispatch for Hoggar Power (Pyomo)."""
import pyomo.environ as pyo
import power_data as d

initially_on = {"Steam": 1, "CCGT1": 1, "CCGT2": 0,
                "OCGT1": 0, "OCGT2": 0, "Diesel": 0}
initial_output = {"Steam": 450, "CCGT1": 380}
reserve_share = 0.10                    # spinning reserve: 10% of demand


def build_model(commitment=True):
    m = pyo.ConcreteModel(name="Unit_Commitment")
    m.U = pyo.Set(initialize=d.names)
    m.T = pyo.Set(initialize=d.hours, ordered=True)
    kind = pyo.Binary if commitment else pyo.UnitInterval

    m.on = pyo.Var(m.U, m.T, domain=kind)          # unit is running
    m.start = pyo.Var(m.U, m.T, domain=kind)       # unit starts at t
    m.stop = pyo.Var(m.U, m.T, domain=kind)        # unit stops at t
    m.p = pyo.Var(m.U, m.T, domain=pyo.NonNegativeReals)   # output, MW
    m.pv = pyo.Var(m.T, domain=pyo.NonNegativeReals)       # solar used
    m.shed = pyo.Var(m.T, domain=pyo.NonNegativeReals)     # unserved load

    @m.Objective()
    def cost(m):
        return sum(d.cost[u] * m.p[u, t] + d.noload[u] * m.on[u, t]
                   + d.startup[u] * m.start[u, t]
                   for u in m.U for t in m.T) + sum(
                       d.voll * m.shed[t] for t in m.T)

    @m.Constraint(m.T)
    def balance(m, t):
        return sum(m.p[u, t] for u in m.U) + m.pv[t] + m.shed[t] \
            == d.demand[t]

    @m.Constraint(m.T)
    def solar_limit(m, t):
        return m.pv[t] <= d.solar[t]

    @m.Constraint(m.T)
    def reserve(m, t):                  # headroom on running units
        return sum(d.pmax[u] * m.on[u, t] - m.p[u, t] for u in m.U) \
            >= reserve_share * d.demand[t]

    @m.Constraint(m.U, m.T)
    def output_max(m, u, t):
        return m.p[u, t] <= d.pmax[u] * m.on[u, t]

    @m.Constraint(m.U, m.T)
    def output_min(m, u, t):
        return m.p[u, t] >= d.pmin[u] * m.on[u, t]

    def prev(m, var, u, t, initial):
        return initial if t == m.T.first() else var[u, m.T.prev(t)]

    @m.Constraint(m.U, m.T)
    def logic(m, u, t):                 # on(t) - on(t-1) = start - stop
        before = prev(m, m.on, u, t, initially_on[u])
        return m.on[u, t] - before == m.start[u, t] - m.stop[u, t]

    @m.Constraint(m.U, m.T)
    def ramp_up(m, u, t):
        before = prev(m, m.p, u, t, initial_output.get(u, 0))
        return m.p[u, t] - before <= d.ramp[u] + d.pmax[u] * m.start[u, t]

    @m.Constraint(m.U, m.T)
    def ramp_down(m, u, t):
        before = prev(m, m.p, u, t, initial_output.get(u, 0))
        return before - m.p[u, t] <= d.ramp[u] + d.pmax[u] * m.stop[u, t]

    @m.Constraint(m.U, m.T)
    def min_up(m, u, t):                # started in the last UT hours => on
        k = d.hours.index(t)
        window = d.hours[max(0, k - d.min_up[u] + 1):k + 1]
        return sum(m.start[u, s] for s in window) <= m.on[u, t]

    @m.Constraint(m.U, m.T)
    def min_down(m, u, t):            # stopped in the last DT hours => off
        k = d.hours.index(t)
        window = d.hours[max(0, k - d.min_down[u] + 1):k + 1]
        return sum(m.stop[u, s] for s in window) <= 1 - m.on[u, t]

    return m

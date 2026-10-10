"""Tools for diagnosing infeasible linear Pyomo models (continuous or
integer variables). Variable bounds and domains are kept as hard limits."""
import pyomo.environ as pyo
from pyomo.opt import TerminationCondition as TC

solver = pyo.SolverFactory("appsi_highs")


def is_feasible(m):
    """True if m has a solution, False if it is proven infeasible. The
    objective is switched off: with the real objective, a model with
    constraints removed may be *unbounded*, which proves nothing."""
    objectives = list(m.component_data_objects(pyo.Objective, active=True))
    for obj in objectives:
        obj.deactivate()
    m._zero = pyo.Objective(expr=0)
    try:
        result = solver.solve(m, load_solutions=False)
    finally:                           # restore the model even on errors
        m.del_component(m._zero)
        for obj in objectives:
            obj.activate()
    cond = result.solver.termination_condition
    if cond == TC.optimal:
        return True
    if cond in (TC.infeasible, TC.infeasibleOrUnbounded):  # objective is 0,
        return False                                       # so infeasible
    raise RuntimeError(f"Feasibility test inconclusive: {cond}")


def elastic_violations(m):
    """Allow every constraint to be violated, minimize total violation,
    and return the constraints that had to be violated (and by how much)."""
    e = m.clone()
    e.viol = pyo.VarList(domain=pyo.NonNegativeReals)
    terms = {}
    for c in list(e.component_data_objects(pyo.Constraint, active=True)):
        lo, body, up = c.lower, c.body, c.upper
        v_lo, v_up = e.viol.add(), e.viol.add()   # below lower, above upper
        c.set_value((lo, body + v_lo - v_up, up))
        terms[c.name] = (v_lo, v_up)
    for obj in e.component_data_objects(pyo.Objective, active=True):
        obj.deactivate()
    e.total_violation = pyo.Objective(expr=sum(e.viol.values()))
    result = solver.solve(e, load_solutions=False)
    if not pyo.check_optimal_termination(result):   # e.g. bad variable bounds
        raise RuntimeError(f"Elastic model not solved: "
                           f"{result.solver.termination_condition}")
    e.solutions.load_from(result)
    amounts = {name: pyo.value(a) + pyo.value(b)
               for name, (a, b) in terms.items()}
    return {name: v for name, v in amounts.items() if v > 1e-6}


def conflict_set(m):
    """Deletion filter: a minimal set of constraints that is infeasible on
    its own (an irreducible infeasible subsystem, IIS), given the variable
    bounds. Returns [] if m is feasible: there is no conflict to explain."""
    if is_feasible(m):
        return []
    candidates = list(m.component_data_objects(pyo.Constraint, active=True))
    needed = []
    try:
        for c in candidates:
            c.deactivate()             # is the model still infeasible?
            if is_feasible(m):
                c.activate()           # no: c is part of the conflict
                needed.append(c.name)
    finally:
        for c in candidates:           # restore the model
            c.activate()
    return needed

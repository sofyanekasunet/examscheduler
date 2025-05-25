"""Scheduler – builds CP-SAT model using matrix-filtered room-session pairs."""
from ortools.sat.python import cp_model
from typing import List, Dict, Set, Tuple
from excel_io import ScheduleOutput

def build_schedule(teachers: List[str], sessions: List[str], rooms: List[str],
                   active_pairs: Set[Tuple[str,str]], backup_ratio: float = 0.2, time_limit: int = 10):
    model = cp_model.CpModel()
    x = {}  # supervisors
    for t in teachers:
        for r, s in active_pairs:
            x[(t, r, s)] = model.NewBoolVar(f"x_{t}_{r}_{s}")
    b = {(t, s): model.NewBoolVar(f"b_{t}_{s}") for t in teachers for s in sessions}

    # two supervisors per active room-session
    for r, s in active_pairs:
        model.Add(sum(x[(t, r, s)] for t in teachers) == 2)

    # no teacher repeats same room
    for t in teachers:
        for r in rooms:
            relevant_sessions = [s for (rr, s) in active_pairs if rr == r]
            if relevant_sessions:
                model.Add(sum(x[(t, r, s)] for s in relevant_sessions) <= 1)

    # at most one duty per session per teacher
    for t in teachers:
        for s in sessions:
            in_rooms = [x[(t, r, s)] for r in rooms if (r, s) in active_pairs]
            model.Add(sum(in_rooms) + b[(t, s)] <= 1)

    # backups per session
    rooms_per_session = {s: sum(1 for r in rooms if (r, s) in active_pairs) for s in sessions}
    for s in sessions:
        backup_needed = int((2 * rooms_per_session[s]) * backup_ratio + 0.999)
        model.Add(sum(b[(t, s)] for t in teachers) == backup_needed)

    # balanced load
    total_slots = 2 * len(active_pairs) + sum(int((2 * rooms_per_session[s]) * backup_ratio + 0.999) for s in sessions)
    avg = (total_slots + len(teachers) - 1) // len(teachers)

    load_vars = {}
    all_sq_diffs = [] # Store squared difference variables for the objective
    for t in teachers:
        load = sum(x_val for ((tt, _r, _s), x_val) in x.items() if tt == t) +                sum(b[(t, s)] for s in sessions)
        load_vars[t] = load
        model.Add(load <= avg + 1)
        model.Add(load >= avg - 1)

        # Auxiliary variables for sum of squares objective
        # diff_t = load_vars[t] - avg, which will be in [-1, 0, 1]
        diff_t_var = model.NewIntVar(-1, 1, f"diff_{t}")
        model.Add(diff_t_var == load_vars[t] - avg)

        # sq_diff_t = diff_t_var * diff_t_var, which will be in [0, 1]
        sq_diff_t_var = model.NewIntVar(0, 1, f"sq_diff_{t}")
        model.AddMultiplicationEquality(sq_diff_t_var, diff_t_var, diff_t_var)
        all_sq_diffs.append(sq_diff_t_var)

    model.Minimize(sum(all_sq_diffs)) # Minimize the sum of squared differences
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible schedule.")

    supervisors = {}
    for (t, r, s), var in x.items():
        if solver.Value(var):
            supervisors.setdefault((r, s), []).append(t)

    backups = {}
    for (t, s), var in b.items():
        if solver.Value(var):
            backups.setdefault(s, []).append(t)

    load_out = {t: int(solver.Value(load_vars[t])) for t in teachers}
    return ScheduleOutput(supervisors=supervisors, backups=backups, load=load_out)
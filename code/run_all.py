"""Run the book's examples and check their results.

    python run_all.py            run and check the examples listed below
    python run_all.py --all      also run the slow ones (several minutes)
    python run_all.py --update   rewrite the stored outputs of "same"
                                 examples, from runs that finished cleanly

Checks run in a temporary copy of this folder, so they never change the
files here. Every example must finish within its time limit with exit
code 0; a crash or a timeout is a failure, and its error output is shown.
What else is checked depends on the kind of example:

  same    the output must match output/<script>.txt line by line, except
          for lines that depend on the computer: run times, the Python
          version and which optional solvers (CBC, GLPK) are installed.
          (Where the book prints only the start of the output, only that
          part is compared.)
  expect  the output varies legitimately between runs (parallel CP-SAT
          searches, equally good solutions), so only the key results are
          checked, with regular expressions that must match some line.
  runs    only a clean finish is required: benchmarks, time-limited
          demonstrations, and scripts that draw the book's figures.

Time-limited routing heuristics (Chapter 11) are compared line by line;
on a much slower computer they may stop at a slightly worse solution.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPDATE, ALL = "--update" in sys.argv, "--all" in sys.argv

OPTIONAL = r"^\s*(PuLP solvers available|CBC|GLPK|cbc|glpk)\b"
same = lambda: {"kind": "same"}
EXAMPLES = {
    "ch01/desks_ortools.py": same(), "ch01/desks_pulp.py": same(),
    "ch01/desks_pyomo.py": same(), "ch01/product_mix.py": same(),
    "ch02/check_install.py": {"kind": "same", "ignore": [r"^Python ", OPTIONAL]},
    "ch02/switch_ortools.py": same(),
    "ch02/switch_pyomo.py": {"kind": "same", "ignore": [OPTIONAL]},
    "ch02/switch_solvers.py": {"kind": "same", "ignore": [OPTIONAL]},
    "ch03/atlas_duals.py": same(), "ch03/atlas_duals_ortools.py": same(),
    "ch03/atlas_duals_pyomo.py": same(), "ch03/atlas_ranging.py": same(),
    "ch03/check_shadow_price.py": same(), "ch03/feed_mix.py": same(),
    "ch03/feed_mix_v1.py": {"kind": "same", "prefix": True},  # partly shown
    "ch03/special_cases.py": same(),
    "ch04/bnb_demo.py": same(), "ch04/formulation_strength.py": same(),
    "ch04/piecewise.py": same(), "ch04/project_selection.py": same(),
    "ch04/rounding.py": same(), "ch04/setup_costs.py": same(),
    "ch05/pitfalls.py": same(), "ch05/snacks.py": same(),
    "ch05/snacks_lexico.py": same(), "ch05/snacks_whatif.py": same(),
    "ch05/write_files.py": same(),
    "ch06/cryptarithm.py": same(), "ch06/snacks_ortools.py": same(),
    "ch06/trucks_cpsat.py": {"kind": "same", "ignore": [r"^Solve time"]},
    "ch06/trucks_mip.py": {"kind": "same", "ignore": [r"^Solve time"]},
    "ch07/atlas_abstract.py": same(), "ch07/modify_pyomo.py": same(),
    "ch07/snacks_pyomo.py": same(), "ch07/snacks_pyomo_scenarios.py": same(),
    "ch08/farm_pulp.py": same(),
    "ch08/farm_ortools.py": {"kind": "same", "stored": "farm_pulp.txt"},
    "ch08/farm_pyomo.py": {"kind": "same", "stored": "farm_pulp.txt"},
    "ch08/benchmark.py": {"kind": "runs", "slow": True},
    "ch09/transport.py": same(), "ch09/transship_pulp.py": same(),
    "ch09/transship_mcf.py": same(), "ch09/assignment.py": same(),
    "ch09/assignment_speed.py": {"kind": "runs", "slow": True},
    "ch10/dc_ufl.py": same(), "ch10/dc_cfl.py": same(),
    "ch10/dc_tradeoff.py": same(), "ch10/dc_two_echelon.py": same(),
    "ch10/dc_map.py": {"kind": "runs"},
    "ch11/tsp_mip.py": same(), "ch11/tsp_routing.py": same(),
    "ch11/cvrp.py": same(), "ch11/vrptw.py": same(),
    "ch11/vrptw_drop.py": same(), "ch11/vrp_map.py": {"kind": "runs"},
    "ch11/tsp_speed.py": {"kind": "runs", "slow": True},
    "ch12/water_plan.py": same(), "ch12/rolling.py": same(),
    "ch12/lot_sizing.py": same(), "ch12/gasoline_blend.py": same(),
    "ch13/column_generation.py": same(),
    "ch13/pattern_figure.py": {"kind": "runs"},
    "ch13/bin_packing.py": {"kind": "expect", "expect": [
        r"^First-fit decreasing: 21 shifts", r"^CP-SAT: 19 shifts, OPTIMAL"]},
    "ch13/cutting_naive.py": {"kind": "runs", "slow": True},
    "ch14/dispatch_hour.py": same(), "ch14/uc_solve.py": same(),
    "ch14/uc_prices.py": same(),
    "ch15/sudoku.py": same(),
    "ch15/exam_timetable.py": {"kind": "expect", "expect": [
        r"student-days with two exams: 369$", r"^Status: OPTIMAL$"]},
    "ch16/shift_starts.py": same(), "ch16/roster_check.py": same(),
    "ch16/roster.py": {"kind": "expect", "check_with": "roster_check.py",
                       "expect": [r"^Status: OPTIMAL  objective 15$"]},
    "ch17/cpm_lp.py": same(),
    "ch17/jobshop.py": {"kind": "expect",
                        "expect": [r"^Status: OPTIMAL, makespan 55$"]},
    "ch17/rcpsp.py": {"kind": "expect", "expect": [
        r"^Status: OPTIMAL, duration 80 working days$"]},
    "ch17/gantt.py": {"kind": "runs"},
    "ch18/capital_budget.py": same(), "ch18/cash_plan.py": same(),
    "ch18/dedication.py": same(),
    "ch19/frontier.py": same(), "ch19/out_of_sample.py": same(),
    "ch19/practical.py": same(),
    "ch20/excel_io.py": same(), "ch20/infeasible_snacks.py": same(),
}


def normalize(text, ignore=()):
    """Drop blank lines and computer-dependent lines; blank out run times."""
    lines = text.splitlines()
    if lines and "time (s)" in lines[0]:          # tables with a time column
        lines = [lines[0]] + [l.rsplit(maxsplit=1)[0] for l in lines[1:]]
    out = []
    for line in lines:
        if not line.strip() or any(re.search(p, line) for p in ignore):
            continue
        out.append(re.sub(r"time = [\d.]+ ?s", "time = ?", line.rstrip()))
    return out


def run(folder, script, timeout, *args):
    try:
        r = subprocess.run([sys.executable, script, *args], cwd=folder,
                           timeout=timeout, capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout} s"


def check(base, name, spec):
    """Return None if the example passes, or a description of the problem."""
    path = base / name
    timeout = 900 if spec.get("slow") else 180
    code, out, err = run(path.parent, path.name, timeout)
    if code != 0:
        return f"exit code {code}\n{err.strip()[-1500:]}"
    if spec["kind"] == "same":
        stored = path.parent / "output" / spec.get("stored", path.stem + ".txt")
        ignore = spec.get("ignore", [])
        want, got = normalize(stored.read_text(), ignore), normalize(out, ignore)
        if spec.get("prefix"):                    # the book prints only the
            got = got[:len(want)]                 # first part of the output
        if got != want:
            for i, (a, b) in enumerate(zip(want + [""] * len(got),
                                           got + [""] * len(want))):
                if a != b:
                    return f"line {i + 1}: expected {a!r}\n{'':>18}got {b!r}"
    if spec["kind"] == "expect":
        missing = [p for p in spec["expect"]
                   if not any(re.search(p, l) for l in out.splitlines())]
        if missing:
            return f"no line matches {missing}"
    if "check_with" in spec:                      # validate the fresh result
        fresh = path.parent / "fresh_output.txt"
        fresh.write_text(out)
        code, cout, cerr = run(path.parent, spec["check_with"], 60, fresh.name)
        if code != 0:
            return f"{spec['check_with']} rejects it:\n{(cout + cerr).strip()}"
    return None


def main():
    failures, skipped = 0, 0
    if UPDATE:
        for name, spec in EXAMPLES.items():
            if spec["kind"] != "same" or "stored" in spec or "prefix" in spec:
                continue                          # nothing of its own to store
            path = ROOT / name
            code, out, err = run(path.parent, path.name, 900)
            if code != 0:                         # never store a failed run
                failures += 1
                print(f"FAIL     {name}  (not updated)\n{err.strip()[-800:]}")
                continue
            (path.parent / "output" / (path.stem + ".txt")).write_text(out)
            print(f"updated  {name}")
        sys.exit(1 if failures else 0)

    with tempfile.TemporaryDirectory() as tmp:    # leave this folder untouched
        base = Path(tmp) / "code"
        shutil.copytree(ROOT, base, ignore=shutil.ignore_patterns(
            "__pycache__", "*.xlsx", "*.lp", "*.mps"))
        for name, spec in EXAMPLES.items():
            if spec.get("slow") and not ALL:
                skipped += 1
                print(f"skip     {name}  (slow; use --all)")
                continue
            problem = check(base, name, spec)
            failures += problem is not None
            label = {"same": "ok", "expect": "ok*", "runs": "ran"}[spec["kind"]]
            print(f"{'FAIL' if problem else label:<9}{name}")
            if problem:
                print("         " + problem.replace("\n", "\n         "))
    print(f"\n{len(EXAMPLES) - skipped} examples run, {failures} failed, "
          f"{skipped} skipped.  ok = output identical, ok* = key results "
          f"checked, ran = finished cleanly.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

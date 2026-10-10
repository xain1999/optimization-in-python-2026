"""Check a printed roster against every hard rule, independently of the
model. A separate checker catches modeling mistakes the solver cannot.
Usage: python roster.py > my_roster.txt; python roster_check.py my_roster.txt
(without an argument, the roster printed in the book is checked)."""
import sys
from roster_data import (nurses, senior, shifts, days, need, min_shifts,
                         max_shifts, max_nights, max_consecutive, no_nights)

path = sys.argv[1] if len(sys.argv) > 1 else "output/roster.txt"
lines = open(path).read().splitlines()
grid = {}
for line in lines:
    name = line[:8].strip()
    if name in nurses:
        grid[name] = line[9:9 + len(days)]

problems = []
for n, row in grid.items():
    work = [c in shifts for c in row]
    if not min_shifts <= sum(work) <= max_shifts:
        problems.append(f"{n}: {sum(work)} shifts")
    nights = row.count("N")
    if nights > (0 if n in no_nights else max_nights):
        problems.append(f"{n}: {nights} nights")
    for d in days[:-1]:
        if row[d] + row[d + 1] in ("NM", "NE", "EM"):
            problems.append(f"{n}: {row[d]} then {row[d + 1]} on day {d}")
    for d in days[:len(days) - max_consecutive]:
        if all(work[d:d + max_consecutive + 1]):
            problems.append(f"{n}: too many days in a row from {d}")
for d in days:
    for s in shifts:
        on = [n for n in grid if grid[n][d] == s]
        if len(on) < need[d, s]:
            problems.append(f"day {d} {s}: {len(on)} < {need[d, s]}")
        if not senior & set(on):
            problems.append(f"day {d} {s}: no senior nurse")

if len(grid) != len(nurses):
    problems.append(f"found {len(grid)} of {len(nurses)} nurses in {path}")
print("All hard rules satisfied." if not problems else "\n".join(problems))
sys.exit(1 if problems else 0)

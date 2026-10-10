# Optimization in Python: PuLP, OR-Tools and Pyomo by Example

Companion code for the book by **Mohammed Islam Hadjoudj**.

Every program printed in the book is here, organized by chapter. Each
chapter folder contains the scripts, any data files they read, and an
`output/` folder with the exact output printed in the book.

## Setup

You need **Python 3.12 or newer** (PuLP 4.0 does not install on older
versions). The examples were tested with Python 3.13.

```bash
python -m venv opt
source opt/bin/activate          # Windows: opt\Scripts\activate
pip install -r requirements.txt
python ch02/check_install.py     # all three libraries should print 8.0
```

`requirements.txt` pins the tested version of every package the examples
import directly: PuLP 4.0.0, OR-Tools 9.15.6755, Pyomo 6.10.1, highspy
1.13.1 (HiGHS), NumPy, SciPy, pandas, matplotlib and openpyxl, plus the
optional CBC (`cbcbox`) and GLPK (`swiglpk`) solvers for PuLP. Their own
dependencies are not pinned. Chapter 2 of the book explains the
installation and the known compatibility issue between new `highspy`
releases and OR-Tools.

`cbcbox` also installs a `cbc` command in the environment's `bin/` folder
(`Scripts\` on Windows). Pyomo's `SolverFactory("cbc")` finds it only while
the environment is activated; the examples do not need it.

The repository contains Python scripts and data files, not notebooks. If you
prefer notebooks, `pip install jupyterlab` and paste a script into a cell.

## Running the examples

Run each script from its own chapter folder, for example:

```bash
cd ch05
python snacks.py
```

`run_all.py` runs the 84 examples listed in it and checks them:

```bash
python run_all.py            # check (about two minutes)
python run_all.py --all      # also the slow benchmarks (several minutes more)
python run_all.py --update   # regenerate the stored outputs
```

Checks run in a temporary copy of the folder, so they never modify your
files. Every example must finish within its time limit with exit code 0;
a crash or timeout is reported with its error output. In addition:

- **ok** - the output matches the output printed in the book
  (`output/<script>.txt`) line by line, apart from run times, the Python
  version and which optional solvers are installed.
- **ok\*** - the output varies legitimately between runs (parallel CP-SAT
  searches can return different, equally good timetables, rosters and
  schedules), so the key results are checked instead: the objective values
  and solver status. Each freshly generated roster is also validated by the
  independent checker `ch16/roster_check.py`.
- **ran** - only a clean finish is required: benchmarks and time-limited
  demonstrations (with `--all`) and the scripts that draw the book's figures.

The routing examples of Chapter 11 use time-limited heuristics; on a much
slower computer they may stop at a slightly different solution.
`--update` only stores output from runs that finished cleanly.

## Contents

| Folder | Chapter |
|--------|---------|
| `ch01` | Thinking in Models |
| `ch02` | Setting Up Your Environment |
| `ch03` | Linear Programming Essentials |
| `ch04` | Integer Programming Essentials |
| `ch05` | PuLP in Depth |
| `ch06` | OR-Tools |
| `ch07` | Pyomo |
| `ch08` | One Problem, Three Libraries |
| `ch09` | Transportation and Assignment Problems |
| `ch10` | Facility Location and Network Design |
| `ch11` | Vehicle Routing with OR-Tools |
| `ch12` | Production Planning, Blending and Inventory |
| `ch13` | Cutting Stock and Bin Packing |
| `ch14` | Energy Dispatch and Unit Commitment |
| `ch15` | Constraint Programming with CP-SAT |
| `ch16` | Staff Rostering and Shift Scheduling |
| `ch17` | Job Shop and Project Scheduling |
| `ch18` | Capital Budgeting and Cash-Flow Planning |
| `ch19` | Portfolio Optimization with Linear Models |
| `ch20` | From Model to Practice |
| `common` | Shared data: approximate coordinates of Algerian cities |

## Notes

- All company names and most data are fictional. City coordinates are
  approximate, and road distances are estimated from them.
- The portfolio data of Chapter 19 are simulated, not market data.
- Nothing in this repository is investment advice.
- Corrections found after publication are listed in `ERRATA.md`.

## License

MIT License. You may use the code freely in your own projects.

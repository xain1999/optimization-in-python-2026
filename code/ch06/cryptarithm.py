"""SEND + MORE = MONEY: each letter is a different digit."""
from ortools.sat.python import cp_model

model = cp_model.CpModel()
letters = "SENDMORY"
d = {c: model.new_int_var(0, 9, c) for c in letters}

model.add_all_different(d.values())
model.add(d["S"] != 0)                       # no leading zeros
model.add(d["M"] != 0)

def word(w):                                 # value of a word, e.g. SEND
    return sum(10 ** i * d[c] for i, c in enumerate(reversed(w)))

model.add(word("SEND") + word("MORE") == word("MONEY"))

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
for w in ["SEND", "MORE", "MONEY"]:
    print(f"{w:>6} = {''.join(str(solver.value(d[c])) for c in w):>6}")

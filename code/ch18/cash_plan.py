"""Six-month cash management: credit line, commercial paper, deposits."""
import pulp

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
net_flow = [-150, -100, 200, -200, 50, 300]    # $k: receipts - payments
T = range(len(months))
line_cap, line_rate = 100, 0.010    # credit line limit, monthly interest
paper_rate = 0.020                  # 3-month commercial paper, total cost
deposit_rate = 0.003                # monthly interest on surplus cash

m = pulp.LpProblem("Cash_Plan", pulp.LpMaximize)
line = m.add_variable_dict("line", T, lowBound=0, upBound=line_cap)
paper = m.add_variable_dict("paper", T, lowBound=0)    # issued in month t
cash = m.add_variable_dict("cash", T, lowBound=0)      # invested surplus

for t in T:
    paper_due = (1 + paper_rate) * paper[t - 3] if t >= 3 else 0
    if t > len(T) - 4:                     # paper must mature by June
        m += paper[t] == 0, f"no_paper_{t}"
    inflow = net_flow[t] + line[t] + paper[t]
    if t > 0:
        inflow += (1 + deposit_rate) * cash[t - 1] \
            - (1 + line_rate) * line[t - 1]
    m += inflow - paper_due == cash[t], f"balance_{months[t]}"
m += line[len(T) - 1] == 0, "repay_line"      # no debt left at the end
m += cash[len(T) - 1]                          # objective: end-of-June cash

m.solve(pulp.HiGHS(msg=False))
print(f"{'month':<6}{'net flow':>9}{'line':>8}{'paper':>8}{'deposit':>9}"
      f"{'value of $1':>13}")
for t in T:
    dual = m.get_constraint_by_name(f"balance_{months[t]}").pi
    print(f"{months[t]:<6}{net_flow[t]:>9}{line[t].value() + 0:>8.1f}"
          f"{paper[t].value() + 0:>8.1f}{cash[t].value():>9.1f}"
          f"{abs(dual):>13.4f}")
print(f"Cash at the end of June: ${pulp.value(m.objective):.2f}k")

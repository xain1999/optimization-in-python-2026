"""Djurdjura Water: monthly demand and costs (thousands of packs)."""
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
demand = dict(zip(months, [420, 400, 460, 520, 640, 820,
                           960, 940, 700, 540, 450, 430]))
regular_cap = 600          # packs per month on regular shifts
overtime_cap = 150         # extra packs per month with overtime
cost_regular = 2.00        # $ per pack
cost_overtime = 2.80       # $ per pack (overtime premium)
cost_hold = 0.15           # $ per pack held at the end of a month
cost_backlog = 1.20        # $ per pack delivered one month late
warehouse_cap = 900        # maximum packs in stock
initial_stock = 100
final_stock = 100          # safety stock to carry into next year

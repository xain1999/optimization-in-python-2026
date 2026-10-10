"""Units, solar output and demand for Hoggar Power (a fictional utility)."""
# unit: (Pmin MW, Pmax MW, energy cost $/MWh, no-load $/h, start-up $,
#        min up h, min down h, ramp MW/h)
units = {
    "Steam":  (200, 500, 38, 2000, 15000, 10, 8, 80),
    "CCGT1":  (150, 400, 42, 1200, 8000, 6, 4, 150),
    "CCGT2":  (150, 400, 44, 1200, 8000, 6, 4, 150),
    "OCGT1":  (30, 150, 85, 300, 1500, 1, 1, 150),
    "OCGT2":  (30, 150, 90, 300, 1500, 1, 1, 150),
    "Diesel": (5, 60, 160, 100, 200, 1, 1, 60),
}
names = list(units)
pmin = {u: v[0] for u, v in units.items()}
pmax = {u: v[1] for u, v in units.items()}
cost = {u: v[2] for u, v in units.items()}
noload = {u: v[3] for u, v in units.items()}
startup = {u: v[4] for u, v in units.items()}
min_up = {u: v[5] for u, v in units.items()}
min_down = {u: v[6] for u, v in units.items()}
ramp = {u: v[7] for u, v in units.items()}

hours = list(range(24))
demand = [880, 850, 830, 820, 830, 880, 960, 1050, 1120, 1170, 1210, 1240,
          1260, 1250, 1230, 1220, 1240, 1300, 1400, 1480, 1500, 1420, 1220,
          1010]                                          # MW, summer day
solar = [0, 0, 0, 0, 0, 0, 20, 90, 170, 240, 290, 320,
         330, 320, 290, 240, 170, 90, 20, 0, 0, 0, 0, 0]  # MW available
voll = 3000                       # $/MWh value of lost load (penalty)

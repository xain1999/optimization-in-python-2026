"""Draw the single-sourcing network as a TikZ picture for the book."""
import dc_data as d
from dc_model import build_model, solve

data = {"fixed": d.fixed, "capacity": d.capacity,
        "demand": d.demand, "cost": d.cost}
m = build_model(data, capacitated=True, single_source=True)
opened, assign = solve(m)

def xy(city):                       # longitude/latitude -> centimetres
    lat, lon = d.CITIES[city]
    return 1.12 * (lon + 2.5), 1.12 * (lat - 31.3)

lines = [r"\begin{tikzpicture}[font=\scriptsize\sffamily]"]
for c, s in assign.items():         # assignment lines
    (x1, y1), (x2, y2) = xy(c), xy(s)
    lines.append(rf"\draw[gray!60] ({x1:.2f},{y1:.2f}) -- ({x2:.2f},{y2:.2f});")
for c, q in d.demand.items():       # cities, size ~ demand
    x, y = xy(c)
    r = 0.04 + 0.0009 * q
    lines.append(rf"\fill[gray!55] ({x:.2f},{y:.2f}) circle ({r:.3f});")
for s in d.fixed:                   # candidate sites
    x, y = xy(s)
    style = "fill=black" if s in opened else "fill=white, draw=black"
    lines.append(rf"\node[{style}, minimum size=5pt, inner sep=0pt] "
                 rf"at ({x:.2f},{y:.2f}) {{}};")
    if s in opened:
        lines.append(rf"\node[below right=1pt, font=\scriptsize\sffamily\bfseries]"
                     rf" at ({x:.2f},{y:.2f}) {{{s}}};")
lines.append(r"\end{tikzpicture}")
with open("output/dc_map.tex", "w") as f:
    f.write("\n".join(lines) + "\n")
print("Map written for:", ", ".join(opened))

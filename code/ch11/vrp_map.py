"""Draw the VRPTW routes as a TikZ picture for the book."""
import subprocess
import sys
from region_data import places, coords

# Re-run vrptw.py and read its routes from the printed output.
out = subprocess.run([sys.executable, "vrptw.py"], capture_output=True,
                     text=True).stdout.splitlines()
routes, current = [], None
for line in out:
    if line.startswith("Truck ") and line[6].isdigit():
        current = []
        routes.append(current)
    elif current is not None and line.startswith("   "):
        name = line[10:].strip()
        current.append("Blida" if name == "back at depot" else name)

def xy(p):                                  # stretched vertically for space
    lat, lon = coords[places.index(p)]
    return 1.55 * (lon + 0.9), 2.4 * (lat - 33.5)

label_pos = {"Algiers": "above", "Tizi Ouzou": "above", "Medea": "below left",
             "Chlef": "above", "Bejaia": "above", "Jijel": "above right",
             "Setif": "right", "Bordj Bou Arreridj": "below",
             "Msila": "below", "Djelfa": "right", "Laghouat": "below",
             "Tiaret": "below", "Relizane": "below right",
             "Mostaganem": "above left", "Mascara": "below left"}
short = {"Bordj Bou Arreridj": "B.B. Arreridj"}

styles = ["solid", "dashed", "dotted", "dashdotted", "densely dashed",
          "loosely dotted"]
lines = [r"\begin{tikzpicture}[font=\scriptsize\sffamily]"]
for k, r in enumerate(routes):
    path = " -- ".join(f"({x:.2f},{y:.2f})" for x, y in map(xy, r))
    lines.append(rf"\draw[thick, {styles[k % len(styles)]}] {path};")
for p in places:
    x, y = xy(p)
    if p == "Blida":
        lines.append(rf"\node[fill=black, minimum size=6pt, inner sep=0pt]"
                     rf" at ({x:.2f},{y:.2f}) {{}};")
        lines.append(rf"\node[below right=2pt, font=\scriptsize\sffamily"
                     rf"\bfseries] at ({x:.2f},{y:.2f}) {{Blida (DC)}};")
    else:
        lines.append(rf"\fill[white, draw=black] ({x:.2f},{y:.2f}) "
                     rf"circle (2pt);")
        lines.append(rf"\node[{label_pos[p]}=1pt] at ({x:.2f},{y:.2f}) "
                     rf"{{{short.get(p, p)}}};")
lines.append(r"\end{tikzpicture}")
with open("output/vrptw_map.tex", "w") as f:
    f.write("\n".join(lines) + "\n")
print(len(routes), "routes drawn")

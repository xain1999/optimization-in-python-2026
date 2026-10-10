"""Draw the cutting patterns found by column generation (TikZ)."""
import re
from rebar_data import bar_length

rows = []
for line in open("output/column_generation.txt"):
    m = re.match(r"\s+(\d+) bars?: (.+?)\s+waste", line)
    if m:
        pieces = [(int(c), int(l)) for c, l in
                  re.findall(r"(\d+)x(\d+)", m.group(2))]
        rows.append((int(m.group(1)), pieces))
rows.sort(key=lambda r: -r[0])

scale = 9.0 / bar_length                 # 12 m bar -> 9 cm
out = [r"\begin{tikzpicture}[font=\scriptsize\sffamily]"]
for k, (n, pieces) in enumerate(rows):
    y, x = -0.62 * k, 0.0
    out.append(rf"\node[left] at (0,{y + 0.2:.2f}) {{{n}$\times$}};")
    for count, length in pieces:
        for _ in range(count):
            w = length * scale
            out.append(rf"\draw[fill=gray!25] ({x:.2f},{y:.2f}) rectangle "
                       rf"({x + w:.2f},{y + 0.4:.2f});")
            out.append(rf"\node at ({x + w / 2:.2f},{y + 0.2:.2f}) "
                       rf"{{{length / 100:g}}};")
            x += w
    if x < 9.0 - 1e-6:                   # waste at the end of the bar
        out.append(rf"\draw[pattern=north east lines] ({x:.2f},{y:.2f}) "
                   rf"rectangle (9,{y + 0.4:.2f});")
out.append(r"\end{tikzpicture}")
open("output/patterns.tex", "w").write("\n".join(out) + "\n")
print(len(rows), "patterns drawn")

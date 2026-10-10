"""Draw Gantt charts (TikZ) from the job-shop and project solutions."""
from project_data import activities, masons_available

shade = ["gray!15", "gray!35", "gray!55", "gray!75", "black!85", "white"]
text = ["black", "black", "black", "white", "white", "black"]

# --- Job shop: one row per machine, one box per operation ---------------
sx, h = 0.21, 0.55                         # cm per time unit, row height
out = [r"\begin{tikzpicture}[font=\scriptsize\sffamily]"]
for line in open("output/jobshop.dat"):
    mach, job, s, d = map(int, line.split())
    y = -mach * (h + 0.15)
    out.append(rf"\draw[fill={shade[job]}] ({s * sx:.2f},{y:.2f}) rectangle "
               rf"({(s + d) * sx:.2f},{y + h:.2f});")
    if d >= 3:
        out.append(rf"\node[text={text[job]}] at ({(s + d / 2) * sx:.2f},"
                   rf"{y + h / 2:.2f}) {{J{job}}};")
for mach in range(6):
    y = -mach * (h + 0.15)
    out.append(rf"\node[left] at (0,{y + h / 2:.2f}) {{M{mach}}};")
for t in range(0, 56, 5):
    out.append(rf"\draw ({t * sx:.2f},-3.6) -- ++(0,-0.08) "
               rf"node[below] {{{t}}};")
out.append(r"\draw (0,-3.6) -- (11.55,-3.6);")
out.append(r"\end{tikzpicture}")
open("output/jobshop_gantt.tex", "w").write("\n".join(out) + "\n")

# --- Project: one row per activity, plus the masons profile -------------
rows = [line.split() for line in open("output/rcpsp.dat")]
rows.sort(key=lambda r: (int(r[1]), r[0]))
sx, h = 0.112, 0.32
out = [r"\begin{tikzpicture}[font=\scriptsize\sffamily]"]
for k, (a, s, d, crew) in enumerate(rows):
    s, d, crew = int(s), int(d), int(crew)
    y = -k * (h + 0.08)
    fill = "black!50" if crew else "black!6"
    crane = activities[a][4]
    out.append(rf"\draw[fill={fill}{', thick' if crane else ''}] "
               rf"({s * sx:.2f},{y:.2f}) rectangle ({(s + d) * sx:.2f},"
               rf"{y + h:.2f});")
    out.append(rf"\node[left] at (0,{y + h / 2:.2f}) "
               rf"{{{a} {activities[a][0]}}};")
base = -len(rows) * (h + 0.08) - 0.5
use = [0] * 81
for a, s, d, crew in rows:
    for t in range(int(s), int(s) + int(d)):
        use[t] += int(crew)
for t in range(80):                        # masons in use, as columns
    if use[t]:
        out.append(rf"\fill[black!50] ({t * sx:.2f},{base:.2f}) rectangle "
                   rf"({(t + 1) * sx:.2f},{base + use[t] * 0.18:.2f});")
out.append(rf"\draw[densely dashed] (0,{base + masons_available * 0.18:.2f})"
           rf" -- ({80 * sx:.2f},{base + masons_available * 0.18:.2f}) "
           rf"node[right] {{{masons_available} masons}};")
out.append(rf"\node[left] at (0,{base + 0.45:.2f}) {{masons in use}};")
for t in range(0, 81, 10):
    out.append(rf"\draw ({t * sx:.2f},{base:.2f}) -- ++(0,-0.08) "
               rf"node[below] {{{t}}};")
out.append(rf"\draw (0,{base:.2f}) -- ({80 * sx:.2f},{base:.2f});")
out.append(r"\end{tikzpicture}")
open("output/rcpsp_gantt.tex", "w").write("\n".join(out) + "\n")
print("Gantt charts written")

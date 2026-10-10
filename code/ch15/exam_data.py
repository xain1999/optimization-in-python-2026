"""Enrolments for the exam-timetabling example (random but reproducible)."""
import random

courses = ["LinAlg", "Analysis", "Probability", "Statistics", "OR",
           "NumMethods", "Graphs", "Optimization", "Stochastic",
           "Algorithms",
           "Databases", "Programming", "DiscreteMath", "Topology",
           "GameTheory", "Simulation"]
# Three programmes, each with typical courses; students pick 4 or 5.
programmes = {
    "Mathematics": ["LinAlg", "Analysis", "Topology", "Probability",
                    "DiscreteMath", "Graphs", "NumMethods"],
    "OR":          ["OR", "Optimization", "Stochastic", "Simulation",
                    "GameTheory", "Statistics", "Graphs", "Probability"],
    "Computing":   ["Algorithms", "Databases", "Programming",
                    "DiscreteMath", "NumMethods", "Graphs", "Statistics"],
}
random.seed(2026)
students = []
for prog, options in programmes.items():
    for _ in range(120):
        students.append(random.sample(options, random.choice([4, 5])))

size = {c: sum(c in s for s in students) for c in courses}
shared = {(a, b): sum(a in s and b in s for s in students)
          for i, a in enumerate(courses) for b in courses[i + 1:]}
slots = list(range(8))                  # 4 days x (morning, afternoon)
seats = 300                             # exam-hall seats per session
unavailable = {"Topology": [0, 1], "GameTheory": [6, 7]}  # lecturer away

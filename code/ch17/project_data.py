"""Building a two-storey health centre: activities, durations, resources."""
# code: (description, duration in working days, predecessors,
#        masons needed, uses the crane)
activities = {
    "A": ("Site preparation", 5, [], 0, False),
    "B": ("Excavation", 6, ["A"], 0, False),
    "C": ("Foundations", 8, ["B"], 4, False),
    "D": ("Ground-floor structure", 12, ["C"], 5, True),
    "E": ("Underground utilities", 6, ["B"], 2, False),
    "F": ("First-floor structure", 12, ["D"], 5, True),
    "G": ("Roof", 7, ["F"], 0, True),
    "H": ("External walls", 10, ["F"], 4, False),
    "I": ("Plumbing rough-in", 8, ["D", "E"], 0, False),
    "J": ("Electrical rough-in", 9, ["D"], 0, False),
    "K": ("Windows and doors", 5, ["H"], 0, False),
    "L": ("Interior plastering", 10, ["H", "I", "J"], 4, False),
    "M": ("Finishes and painting", 9, ["G", "K", "L"], 0, False),
    "N": ("Landscaping", 6, ["H"], 2, False),
    "O": ("Inspection and handover", 2, ["M", "N"], 0, False),
}
masons_available = 5

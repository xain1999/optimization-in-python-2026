"""Shared data for the truck-loading examples of Chapter 6."""
# pallet: (weight kg, value $, type)
pallets = {
    "P01": (420, 900, "food"),     "P02": (310, 640, "food"),
    "P03": (550, 1150, "general"), "P04": (280, 520, "general"),
    "P05": (390, 860, "chemical"), "P06": (460, 980, "food"),
    "P07": (230, 410, "general"),  "P08": (510, 1020, "chemical"),
    "P09": (340, 700, "food"),     "P10": (600, 1240, "general"),
    "P11": (270, 590, "food"),     "P12": (480, 930, "general"),
    "P13": (360, 760, "chemical"), "P14": (300, 610, "general"),
    "P15": (440, 880, "food"),
}
trucks = {"T1": 1500, "T2": 1500, "T3": 1200}     # weight capacity, kg
max_pallets = 4                                   # floor positions per truck

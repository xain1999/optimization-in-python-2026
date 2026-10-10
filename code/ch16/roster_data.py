"""Two-week roster for a hospital ward: nurses, shifts and requests."""
nurses = ["Amel", "Bachir", "Camelia", "Djamila", "Fares", "Ghania",
          "Hichem", "Imene", "Karim", "Lina", "Mourad", "Nadia",
          "Omar", "Rania"]
senior = {"Amel", "Camelia", "Fares", "Karim", "Nadia"}
shifts = ["M", "E", "N"]                      # morning, evening, night
days = list(range(14))                        # day 0 is a Saturday
weekend = {0, 6, 7, 13}                       # Fridays and Saturdays

need = {}                                     # nurses required per shift
for d in days:
    busy = d not in weekend
    need[d, "M"] = 5 if busy else 3
    need[d, "E"] = 3 if busy else 2
    need[d, "N"] = 2
min_shifts, max_shifts = 9, 10                # per nurse in two weeks
max_nights = 4
max_consecutive = 5

# Requests: (nurse, day) the nurse would like off, with a weight.
day_off_requests = {("Amel", 3): 2, ("Bachir", 6): 2, ("Djamila", 7): 3,
                    ("Djamila", 8): 3, ("Ghania", 0): 1, ("Imene", 10): 2,
                    ("Karim", 13): 1, ("Lina", 4): 2, ("Mourad", 11): 3,
                    ("Omar", 1): 1, ("Rania", 12): 2, ("Hichem", 9): 1,
                    ("Camelia", 4): 2, ("Fares", 4): 1, ("Nadia", 4): 3}
no_nights = {"Djamila", "Lina"}               # medical restriction

# Durées autorisées (secondes)
ALLOWED_DURATIONS = [60, 300, 900]

#limites des mises
STAKE_MIN = 100      # mise minimum (XAF)
STAKE_MAX = 1_000_000  # mise maximum (XAF)

# Règle d'égalité (close_price == open_price)
# False => égalité = PERDANT (LOST) ; True => égalité = DRAW (pnl = 0)
DRAW_ON_EQUAL = False
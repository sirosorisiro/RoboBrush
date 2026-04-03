import math

ALPHA   = 100        # height of 1st axle
BETA    = 75        # dist between axles 
GAMMA   = 110        # horizontal length from 2nd axle to actuator 
C       = 0.504        # angle at 2nd axle
EPSILON = 15        # distance from lin-act to center axis

def curve_point(t: float) -> tuple[float, float]:
    x = 1.0 / (0.15 * t + 0.023) + 185.0
    y = 50.0 - 100.0 * t
    return x, y

def arctan2_desmos(x: float, y: float) -> float:
    """
    Desmos definition (note argument order is Arctan2(x, y), i.e. x is the
    'condition' variable and y is the numerator of the fraction y/x):

        Arctan2(x, y) =
            arctan(y/x)       if x >= 0
            arctan(y/x) + π   if x < 0  AND  x·y <= 0   [2nd/4th quadrant cross]
            arctan(y/x) − π   if x < 0

    This is equivalent to Python's math.atan2(y, x) in all standard cases,
    but we replicate the Desmos piecewise form exactly.
    """
    if x >= 0:
        return math.atan(y / x) if x != 0 else (math.pi / 2 if y > 0 else -math.pi / 2)
    elif x * y <= 0:          # x < 0 and xy <= 0
        return math.atan(y / x) + math.pi
    else:                     # x < 0 and xy > 0
        return math.atan(y / x) - math.pi

def d_diag(eps: float, delta: float) -> float:
    """
    d_diag(ε, δ) = sqrt( (γ + δ)² + ε² )
    """
    return math.sqrt((GAMMA + delta) ** 2 + eps ** 2)


# ── Helper: phi angle ─────────────────────────────────────────────────────────
def phi(eps: float, delta: float) -> float:
    """
    φ(ε, δ) = arctan( ε / (γ + δ) ) + c
    """
    return math.atan(eps / (GAMMA + delta)) + C


# ── Main function ──────────────────────────────────────────────────────────────
def calculate(t: float) -> dict:
    px, py = curve_point(t)
    discriminant = px**2 + py**2 - (BETA * math.sin(C) - EPSILON) ** 2
    if discriminant < 0:
        raise ValueError(
            f"Negative discriminant ({discriminant:.6f}) at t={t}: "
            "point P is outside the reachable workspace."
        )
    u = -BETA * math.cos(C) + math.sqrt(discriminant)
    delta = u - GAMMA
    f = BETA + u * math.cos(C) - EPSILON * math.sin(C)
    g = u * math.sin(C) + EPSILON * math.cos(C)
    x_arg = f * px - g * py
    y_arg = f * py + g * px
    theta1 = arctan2_desmos(x_arg, y_arg)

    p3x = BETA * math.cos(theta1)
    p3y = BETA * math.sin(theta1)

    def arm_endpoint(eps, d):
        """P3 + d_diag(eps,d) · (cos(θ₁ − φ(eps,d)), sin(θ₁ − φ(eps,d)))"""
        angle = theta1 - phi(eps, d)
        dist  = d_diag(eps, d)
        return p3x + dist * math.cos(angle), p3y + dist * math.sin(angle)

    p4 = arm_endpoint(EPSILON,  0)
    p5 = arm_endpoint(EPSILON, -40)
    p6 = arm_endpoint(0,       -40)

    return {
        "delta":  delta,
        "theta1": theta1,
        "P":  (px, py),
        "u": u,
        "f": f,
        "g": g,
        "P1": (0, -ALPHA),
        "P2": (0,  0),
        "P3": (p3x, p3y),
        "P4": p4,
        "P5": p5,
        "P6": p6,
    }

table = [[0 for j in range(4)] for i in range(20)]
def init_lookup_table():
    length = 0.0
    angle = 0.0
    length_last = 0.0
    angle_last = 0.0
    for i in range(20):
        buf = calculate(i/20)
        length_last = length
        angle_last = angle
        length = buf["delta"]
        angle = buf["theta1"]
        table[i][0] = length
        table[i][1] = angle
        table[i][2] = length - length_last
        table[i][3] = angle - angle_last

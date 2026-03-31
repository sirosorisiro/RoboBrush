import math
ALPHA   = 100        # α
BETA    = 75         # β
GAMMA   = 110        # γ
C       = 0.504      # c  (radians)
EPSILON = 15         # ε
R       = 15         # r

T1 = 0.2383


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
    """
    Given parameter t, compute δ (delta) and θ₁ (theta1) plus all
    intermediate and derived quantities.

    Returns a dictionary with every named value so callers can inspect
    intermediate results if needed.
    """

    # Moving point P at parameter t
    px, py = curve_point(t)

    # ── u ─────────────────────────────────────────────────────────────────────
    # u = −β·cos(c) + sqrt( Px² + Py² − (β·sin(c) − ε)² )
    discriminant = px**2 + py**2 - (BETA * math.sin(C) - EPSILON) ** 2
    if discriminant < 0:
        raise ValueError(
            f"Negative discriminant ({discriminant:.6f}) at t={t}: "
            "point P is outside the reachable workspace."
        )
    u = -BETA * math.cos(C) + math.sqrt(discriminant)

    # ── δ (delta) ─────────────────────────────────────────────────────────────
    # δ = u − γ
    delta = u - GAMMA

    # ── f, g intermediate values ──────────────────────────────────────────────
    # f = β + u·cos(c) − ε·sin(c)
    # g = u·sin(c) + ε·cos(c)
    f = BETA + u * math.cos(C) - EPSILON * math.sin(C)
    g = u * math.sin(C) + EPSILON * math.cos(C)

    # ── θ₁ (theta1) ───────────────────────────────────────────────────────────
    # θ₁ = Arctan2( f·Px − g·Py ,  f·Py + g·Px )
    #
    # Desmos: Arctan2(x_arg, y_arg) where
    #   x_arg = f·P.x − g·P.y
    #   y_arg = f·P.y + g·P.x
    x_arg = f * px - g * py
    y_arg = f * py + g * px
    theta1 = arctan2_desmos(x_arg, y_arg)

    # ── Derived geometry (P3, P4, P5, P6) ────────────────────────────────────
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
        # Primary outputs
        "delta":  delta,
        "theta1": theta1,
        # Moving input point
        "P":  (px, py),
        # Intermediate scalars
        "u": u,
        "f": f,
        "g": g,
        # Geometry
        "P1": (0, -ALPHA),
        "P2": (0,  0),
        "P3": (p3x, p3y),
        "P4": p4,
        "P5": p5,
        "P6": p6,
    }


# ── Quick smoke-test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import pprint

    # Evaluate at the reference t₁ value defined in Desmos
    result = calculate(T1)

    print(f"t  = {T1}")
    print(f"δ  (delta)  = {result['delta']:.6f}")
    print(f"θ₁ (theta1) = {result['theta1']:.6f}  rad  "
          f"({math.degrees(result['theta1']):.4f}°)")
    print("\nFull result dict:")
    pprint.pprint({k: (round(v, 6) if isinstance(v, float)
                       else tuple(round(c, 6) for c in v) if isinstance(v, tuple)
                       else v)
                   for k, v in result.items()})

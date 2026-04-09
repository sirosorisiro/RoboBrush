import math
# the functions in this file translate a curve in cartesian space into an array of motor angle and length values
# https://www.desmos.com/calculator/70u4imysat

ALPHA   = 100        # height of 1st axle
BETA    = 75        # dist between axles 
GAMMA   = 213        # horizontal length from 2nd axle to actuator 
C       = 1.5708        # angle at 2nd axle
EPSILON = -60       # distance from lin-act to center axis

def curve_point(t: float) -> tuple[float, float]: # r
    x = 1.0 / (0.15 * t + 0.023) + 250.0
    y = 50.0 - 100.0 * t
    return x, y

divs = 50        # approximate curve with this many straight lines

def arctan2_desmos(x: float, y: float) -> float:
    #helper for calculations, https://en.wikipedia.org/wiki/Atan2
    if x >= 0:
        return math.atan(y / x) if x != 0 else (math.pi / 2 if y > 0 else -math.pi / 2)
    elif x * y <= 0:          # x < 0 and xy <= 0
        return math.atan(y / x) + math.pi
    else:                     # x < 0 and xy > 0
        return math.atan(y / x) - math.pi

def diag_len(eps: float, delta: float) -> float:
    return math.sqrt((GAMMA + delta) ** 2 + eps ** 2)


# fixed second angle of arm 
def phi(eps: float, delta: float) -> float:
    return math.atan(eps / (GAMMA + delta)) + C


def calculate(t: float) -> dict:
    px, py = curve_point(t)
    discriminant = px**2 + py**2 - (BETA * math.sin(C) - EPSILON) ** 2
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
        angle = theta1 - phi(eps, d)
        dist  = diag_len(eps, d)
        return p3x + dist * math.cos(angle), p3y + dist * math.sin(angle)

    p4 = arm_endpoint(EPSILON,  0)
    p5 = arm_endpoint(EPSILON, -40)
    p6 = arm_endpoint(0,       -40)

    return {
        "delta":  delta, # actuator length
        "theta1": theta1, # angle
        "P":  (px, py),   # these points sketch out the device assembly
        "P1": (0, -ALPHA),
        "P2": (0,  0),
        "P3": (p3x, p3y),
        "P4": p4,
        "P5": p5,
        "P6": p6,
    }

table = [[0 for j in range(4)] for i in range(divs)]
def init_lookup_table():
    length = 0.0
    angle = 0.0
    length_last = 0.0
    angle_last = 0.0
    for i in range(divs):
        buf = calculate(i/divs)
        length_last = length
        angle_last = angle
        length = buf["delta"]
        angle = buf["theta1"]
        table[i][0] = length
        table[i][1] = angle
        table[i][2] = length - length_last
        table[i][3] = angle - angle_last

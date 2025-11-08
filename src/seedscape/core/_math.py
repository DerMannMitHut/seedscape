from math import floor as floor, log10 as log10


def sround(x: float, significant: int) -> float:
    if x == 0:
        return 0
    else:
        return round(x, significant - floor(log10(abs(x))) - 1)


def fade(t: float) -> float:
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def axial_to_plane(q, r):
    x = q + 0.5 * r
    y = 0.8660254037844386 * r  # √3/2
    return x, y

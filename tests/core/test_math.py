import math

from seedscape.core import _math


def test_sround_zero_returns_zero():
    assert _math.sround(0.0, 3) == 0


def test_sround_positive_scales_correctly():
    assert _math.sround(1234.567, 1) == 1000
    assert _math.sround(1234.567, 2) == 1200
    assert _math.sround(1234.567, 3) == 1230


def test_sround_small_numbers_significant_digits():
    assert _math.sround(0.01234, 2) == 0.012
    assert _math.sround(0.00999, 1) == 0.01


def test_sround_negative_numbers_bankers_rounding_behavior():
    assert _math.sround(-9876.5, 3) == -9880


def test_fade_endpoints_and_midpoint():
    assert _math.fade(0.0) == 0.0
    assert _math.fade(1.0) == 1.0
    assert math.isclose(_math.fade(0.5), 0.5, rel_tol=0, abs_tol=1e-12)


def test_lerp_basic_properties():
    assert _math.lerp(2.0, 10.0, 0.0) == 2.0
    assert _math.lerp(2.0, 10.0, 1.0) == 10.0
    assert _math.lerp(2.0, 10.0, 0.5) == 6.0


def test_axial_to_plane_known_points():
    x, y = _math.axial_to_plane(0, 0)
    assert x == 0
    assert y == 0

    x, y = _math.axial_to_plane(1, 0)
    assert x == 1
    assert y == 0

    x, y = _math.axial_to_plane(0, 1)
    assert math.isclose(x, 0.5, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(y, 0.8660254037844386, rel_tol=0, abs_tol=1e-12)

    x, y = _math.axial_to_plane(2, -2)
    assert math.isclose(x, 1.0, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(y, -1.7320508075688772, rel_tol=0, abs_tol=1e-12)

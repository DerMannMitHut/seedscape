from __future__ import annotations

import math

import pytest

from seedscape.core.noise import DIRECTIONS, Noise, NoiseType


def test_noise_is_deterministic_and_differ() -> None:
    values = set()
    count = 0
    for seed in ["s1", "another-seed", "🔑"]:
        for ntype in NoiseType:
            for q, r in [(0, 0), (3, -2), (-5, 7), (123456789, -987654321)]:
                values.add(Noise(seed).noise(ntype, q, r))
                values.add(Noise(seed).noise(ntype, q, r))
                count += 1
    assert len(values) == count


@pytest.mark.parametrize("coords", [(0, 0), (1, 2), (-2, 1), (-10, -10)])
def test_noise_in_unit_interval_and_accepts_negatives(coords: tuple[int, int]) -> None:
    n = Noise("seed")
    for ntype in NoiseType:
        v = n.noise(ntype, *coords)
        assert 0.0 <= v <= 1.0


@pytest.mark.parametrize("coords", [(0, 0), (4, -1), (-3, 8)])
def test_smooth_noise_interpolation_extremes(coords: tuple[int, int]) -> None:
    q, r = coords
    n = Noise("seed")
    center = n.noise(NoiseType.altitude, q, r)
    neighbors = [n.noise(NoiseType.altitude, q + dq, r + dr) for dq, dr in DIRECTIONS]
    mean_neighbors = sum(neighbors) / len(neighbors)

    s0 = n.smooth_noise(NoiseType.altitude, q, r, smooth_frac=0.0)
    s1 = n.smooth_noise(NoiseType.altitude, q, r, smooth_frac=1.0)

    assert s0 == center
    assert s1 == pytest.approx(mean_neighbors, rel=1e-15, abs=1e-15)


@pytest.mark.parametrize("bad", [-0.1, 1.1, math.inf, -math.inf])
def test_smooth_noise_raises_on_out_of_range_fraction(bad: float) -> None:
    n = Noise("seed")
    with pytest.raises(ValueError):
        _ = n.smooth_noise(NoiseType.altitude, 0, 0, bad)

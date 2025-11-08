import hashlib
import math

import pytest

from seedscape.core import noise


class _Campaign:
    def __init__(self, seed: str):
        self.seed = seed


def test_normalize_sizes():
    key = noise._get_blake2b_key("abc")
    salt = noise._get_blake2b_salt("kind")
    person = noise._get_blake2b_person("person")
    assert isinstance(key, (bytes, bytearray)) and len(key) == hashlib.blake2b.MAX_KEY_SIZE
    assert isinstance(salt, (bytes, bytearray)) and len(salt) == hashlib.blake2b.SALT_SIZE
    assert isinstance(person, (bytes, bytearray)) and len(person) == hashlib.blake2b.PERSON_SIZE


def test_noiseconfig_freq_base_validation():
    # Allowed upper edge 1, zero is invalid by design (0..1]
    cfg1 = noise.NoiseConfig("x", freq_base=1.0, octaves=1, lacunarity=2.0, gain=0.5)
    assert math.isclose(cfg1.freq_base, 1.0)

    for bad in (-0.001, 0.0, 1.001):
        with pytest.raises(ValueError):
            noise.NoiseConfig("x", freq_base=bad, octaves=1, lacunarity=2.0, gain=0.5)


def test_noisetype_defaults_and_salts():
    alt_cfg = noise.NoiseType.altitude.value
    hum_cfg = noise.NoiseType.humidity.value
    assert isinstance(alt_cfg, noise.NoiseConfig)
    assert isinstance(hum_cfg, noise.NoiseConfig)

    assert alt_cfg.salt == noise._get_blake2b_salt("altitude")
    assert hum_cfg.salt == noise._get_blake2b_salt("humidity")


def test_shuffle_and_hash01_deterministic_and_range():
    n = noise.Noise(_Campaign("seed-1"))
    cfg = noise.NoiseType.altitude.value

    s1 = n._shuffle(cfg, 3, 5)
    s2 = n._shuffle(cfg, 3, 5)
    assert s1 == s2

    s3 = n._shuffle(cfg, 4, 5)
    assert s1 != s3

    h = n._hash01(cfg, 7, -2)
    assert 0.0 <= h < 1.0


def test_hex_noise_range_and_determinism():
    camp = _Campaign("seed-xyz")
    n1 = noise.Noise(camp)
    n2 = noise.Noise(camp)
    cfg = noise.NoiseType.altitude.value

    v11 = n1.hex_noise(cfg, 10, -4)
    v12 = n2.hex_noise(cfg, 10, -4)
    assert 0.0 <= v11 <= 1.0
    assert math.isclose(v11, v12, rel_tol=0, abs_tol=0)

    v2 = n1.hex_noise(cfg, 11, -4)
    assert v11 != v2

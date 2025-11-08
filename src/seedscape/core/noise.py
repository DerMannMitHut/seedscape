import hashlib
from dataclasses import dataclass
from enum import Enum

from seedscape.core import _math
from seedscape.core.models import CampaignMeta


def _normalize_key(seed: str) -> bytes:
    return hashlib.blake2b(seed.encode("utf-8"), digest_size=hashlib.blake2b.MAX_KEY_SIZE).digest()


def _normalize_salt(kind: str) -> bytes:
    return hashlib.blake2b(kind.encode("utf-8"), digest_size=hashlib.blake2b.SALT_SIZE).digest()


def _normalize_person(person: str) -> bytes:
    return hashlib.blake2b(person.encode("utf-8"), digest_size=hashlib.blake2b.PERSON_SIZE).digest()


@dataclass
class NoiseConfig:
    salt: bytes
    freq_base: float
    octaves: int
    lacunarity: float
    gain: float

    def __init__(self, salt: str, freq_base: float, octaves: int, lacunarity: float, gain: float):
        self.salt = _normalize_salt(salt)

        if freq_base < 0 or freq_base > 1:
            raise ValueError(f"freq_base expected from [0..1], but is {freq_base}")
        self.freq_base = freq_base

        self.octaves = octaves
        self.lacunarity = lacunarity
        self.gain = gain


class NoiseType(Enum):
    altitude = NoiseConfig("altitude", freq_base=0.05, octaves=4, lacunarity=2.0, gain=0.5)
    humidity = NoiseConfig("humidity", freq_base=0.05, octaves=4, lacunarity=2.0, gain=0.5)


PERSON = _normalize_person("SeedScape")
DIRECTIONS = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
MIN_ALTITUDE = -100
MAX_ALTITUDE = 10000
HEX_DIAMETER = 5000
HEX_ROW_DISTANCE = HEX_DIAMETER * 0.75
MAX_TEMP_DIFF = 1
MIN_TEMP_DIFF = -1


class Noise:
    def __init__(self, campaign: CampaignMeta):
        self.__key = _normalize_key(campaign.seed)
        self._campaign = campaign

    def _shuffle(self, nconfig: NoiseConfig, *values: int) -> int:
        h = hashlib.blake2b(key=self.__key, salt=nconfig.salt, person=PERSON, digest_size=8)
        for v in values:
            h.update(v.to_bytes(8, "big", signed=True))
        return int.from_bytes(h.digest(), "big", signed=False)

    def _hash01(self, nconfig: NoiseConfig, q: int, r: int) -> float:
        shuffled = self._shuffle(nconfig, q, r)
        return shuffled / 2**64

    def _value_noise(self, nconfig: NoiseConfig, u: float, v: float):
        i = _math.floor(u)
        j = _math.floor(v)
        du = u - i
        dv = v - j

        v00 = self._hash01(nconfig, i, j)
        v10 = self._hash01(nconfig, i + 1, j)
        v01 = self._hash01(nconfig, i, j + 1)
        v11 = self._hash01(nconfig, i + 1, j + 1)

        sx = _math.fade(du)
        sy = _math.fade(dv)
        a = _math.lerp(v00, v10, sx)
        b = _math.lerp(v01, v11, sx)
        return _math.lerp(a, b, sy)

    def hex_noise(self, nconfig: NoiseConfig, q: int, r: int):
        x, y = _math.axial_to_plane(q, r)
        amp, total, freq = 1.0, 0.0, nconfig.freq_base
        amp_sum = 0.0
        for _ in range(nconfig.octaves):
            total += amp * self._value_noise(nconfig, x * freq, y * freq)
            amp_sum += amp
            amp *= nconfig.gain
            freq *= nconfig.lacunarity
        n = total / amp_sum  # ~0..1
        return n

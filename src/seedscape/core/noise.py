import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from seedscape.core import _math

if TYPE_CHECKING:  # avoid importing heavy pydantic models at runtime
    from seedscape.core.models import CampaignMeta


def _get_blake2b_key(seed: str) -> bytes:
    return hashlib.blake2b(seed.encode("utf-8"), digest_size=hashlib.blake2b.MAX_KEY_SIZE).digest()


def _get_blake2b_salt(kind: str) -> bytes:
    return hashlib.blake2b(kind.encode("utf-8"), digest_size=hashlib.blake2b.SALT_SIZE).digest()


def _get_blake2b_person(person: str) -> bytes:
    return hashlib.blake2b(person.encode("utf-8"), digest_size=hashlib.blake2b.PERSON_SIZE).digest()


@dataclass(frozen=True)
class NoiseConfig:
    salt_label: str
    freq_base: float
    octaves: int
    lacunarity: float
    gain: float
    # Derived from salt_label; used by blake2b as salt
    salt: bytes = field(init=False)

    def __post_init__(self):
        # Validate parameters
        if self.freq_base <= 0 or self.freq_base > 1:
            raise ValueError(f"freq_base expected from (0..1], but is {self.freq_base}")
        if self.octaves < 1:
            raise ValueError(f"octaves expected to be 1 or greater, but is {self.octaves}")
        # Compute salt bytes from the label
        object.__setattr__(self, "salt", _get_blake2b_salt(self.salt_label))


class NoiseType(Enum):
    altitude = NoiseConfig("altitude", freq_base=0.05, octaves=4, lacunarity=2.0, gain=0.5)
    humidity = NoiseConfig("humidity", freq_base=0.05, octaves=4, lacunarity=2.0, gain=0.5)


PERSON = _get_blake2b_person("SeedScape")
DIRECTIONS = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
HEX_DIAMETER = 5000


class Noise:
    def __init__(self, campaign: "CampaignMeta"):
        self._key = _get_blake2b_key(campaign.seed)
        self._campaign = campaign

    def _shuffle(self, nconfig: NoiseConfig, *values: int) -> int:
        h = hashlib.blake2b(key=self._key, salt=nconfig.salt, person=PERSON, digest_size=8)
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

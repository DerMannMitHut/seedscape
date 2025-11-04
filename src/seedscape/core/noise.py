import hashlib
import statistics
from enum import Enum


def _normalize_key(seed: str) -> bytes:
    return hashlib.blake2b(seed.encode("utf-8"), digest_size=hashlib.blake2b.MAX_KEY_SIZE).digest()


def _normalize_salt(kind: str) -> bytes:
    return hashlib.blake2b(kind.encode("utf-8"), digest_size=hashlib.blake2b.SALT_SIZE).digest()


def _normalize_person(person: str) -> bytes:
    return hashlib.blake2b(person.encode("utf-8"), digest_size=hashlib.blake2b.PERSON_SIZE).digest()


class NoiseType(Enum):
    altitude = _normalize_salt("altitude")
    temperature = _normalize_salt("temperature")
    humidity = _normalize_salt("humidity")


PERSON = _normalize_person("SeedScape")
DIRECTIONS = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]


class Noise:
    def __init__(self, seed: str):
        self.__key = _normalize_key(seed)

    def _shuffle(self, ntype: NoiseType, *values: int) -> int:
        h = hashlib.blake2b(key=self.__key, salt=ntype.value, person=PERSON, digest_size=8)
        for v in values:
            h.update(v.to_bytes(8, "big", signed=True))
        return int.from_bytes(h.digest(), "big", signed=False)

    def noise(self, ntype: NoiseType, q: int, r: int) -> float:
        shuffled = self._shuffle(ntype, q, r)
        return shuffled / 2**64

    def smooth_noise(self, ntype: NoiseType, q: int, r: int, smooth_frac: float) -> float:
        if smooth_frac < 0 or smooth_frac > 1:
            raise ValueError(f"0 <= fraction={smooth_frac} <= 1 violated")

        noise_qr = self.noise(ntype, q, r)
        noise_neighbors = statistics.mean(self.noise(ntype, q + dq, r + dr) for dq, dr in DIRECTIONS)

        return noise_neighbors * smooth_frac + noise_qr * (1 - smooth_frac)

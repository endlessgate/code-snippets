
import os
import unicodedata
import hashlib

from cachetools import (
    cached,
    LRUCache,
)

from typing import (
    Union,
    Tuple,
)
from .utils import to_tuple

path = os.path.dirname(__file__)


@cached(cache=LRUCache(1))
@to_tuple
def read_words() -> Tuple[str]:
    with open(f"{path}/wordlist.txt", 'r', encoding='utf-8') as f:
        for word in f.readlines():
            yield word.strip()


def hexdigest(x) -> str:
    return hashlib.sha3_256(x).hexdigest()


def normalize(x: Union[str, bytes]) -> str:
    if isinstance(x, bytes):
        x = x.decode()
    return unicodedata.normalize("NFKD", x)


def generate_random(x: int) -> bytes:
    return os.urandom(x // 8)


@to_tuple
def get_words(binary) -> Tuple[str]:
    words = read_words()

    for i in range(len(binary) // 11):
        index = int(binary[i * 11: (i+1) * 11], 2)
        yield words[index]


def as_mnemonic(salt) -> Tuple[str]:
    if len(salt) not in [16, 20, 24, 28, 32]:
        raise TypeError("size typeof [16, 20, 24, 28, 32]")

    hashes = hexdigest(salt)

    left = bin(int(salt.hex(), 16))[2:].zfill(len(salt) * 8)
    right = bin(int(hashes, 16))[2:].zfill(256)[: len(salt) * 8 // 32]

    binary = left + right
    return get_words(binary)


def as_entropy(words: Union[list, tuple, str]):
    if isinstance(words, str):
        words = words.split()

    if len(words) not in [12, 15, 18, 21, 24]:
        raise TypeError("size typeof [12, 15, 18, 21, 24]")

    mnemolen = len(words) * 11
    mnemo_bits = [b'\x00'] * mnemolen
    index = 0

    ...


def generate_seed(mnemonic, salt=""):
    mnemonic = normalize(mnemonic)
    passphrase = "mnemonic" + normalize(salt)

    stretched = hashlib.pbkdf2_hmac(
        "sha512",
        mnemonic.encode(),
        passphrase.encode(),
        2048
    )
    return stretched[:64]


def generate_master_key():
    ...


def make(size=128):
    if size not in [128, 160, 192, 224, 256]:
        raise TypeError("size typeof [128, 160, 192, 224, 256]")
    rbits = generate_random(size)
    return as_mnemonic(rbits)



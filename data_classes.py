from __future__ import \
    annotations  # PEP 563: Postponed Evaluation of Annotations

from dataclasses import \
    dataclass  # https://docs.python.org/3/library/dataclasses.html I like these a lot

from hash_utils import b58encode, ripemd160, sha256


@dataclass
class Curve:
    """
    Elliptic Curve over the field of integers modulo a prime.
    Points on the curve satisfy y^2 = x^3 + a*x + b (mod p).
    """

    p: int  # the prime modulus of the finite field
    a: int
    b: int


@dataclass
class Point:
    """An integer point (x,y) on a Curve"""

    curve: Curve
    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        """elliptic_curve_addition"""

        def extended_euclidean_algorithm(a, b):
            """
            Returns (gcd, x, y) s.t. a * x + b * y == gcd
            This function implements the extended Euclidean
            algorithm and runs in O(log b) in the worst case,
            taken from Wikipedia.
            """
            old_r, r = a, b
            old_s, s = 1, 0
            old_t, t = 0, 1
            while r != 0:
                quotient = old_r // r
                old_r, r = r, old_r - quotient * r
                old_s, s = s, old_s - quotient * s
                old_t, t = t, old_t - quotient * t
            return old_r, old_s, old_t

        def inv(n, p):
            """returns modular multiplicate inverse m s.t. (n * m) % p == 1"""
            gcd, x, y = extended_euclidean_algorithm(
                n, p
            )  # pylint: disable=unused-variable
            return x % p

        if self == Point(None, None, None):
            return other
        if other == Point(None, None, None):
            return self
        # handle special case of P + (-P) = 0
        if self.x == other.x and self.y != other.y:
            return Point(None, None, None)
        # compute the "slope"
        if self.x == other.x:  # (self.y = other.y is guaranteed too per above check)
            m = (3 * self.x**2 + self.curve.a) * inv(2 * self.y, self.curve.p)
        else:
            m = (self.y - other.y) * inv(self.x - other.x, self.curve.p)
        # compute the new point
        rx = (m**2 - self.x - other.x) % self.curve.p
        ry = (-(m * (rx - self.x) + self.y)) % self.curve.p
        return Point(self.curve, rx, ry)

    def __rmul__(self, k: int) -> Point:
        """Double-and-add algorithm"""
        assert isinstance(k, int) and k >= 0
        result = Point(None, None, None)
        append = self
        while k:
            if k & 1:
                result += append
            append += append
            k >>= 1
        return result


@dataclass
class Generator:
    """
    A generator over a curve: an initial point and the (pre-computed) order
    """

    G: Point  # a generator point on the curve
    n: int  # the order of the generating point, so 0*G = n*G = INF


class PublicKey(Point):
    """
    The public key is just a Point on a Curve, but has some additional specific
    encoding / decoding functionality that this class implements.
    """

    @classmethod
    def from_point(cls, pt: Point):
        """promote a Point to be a PublicKey"""
        return cls(pt.curve, pt.x, pt.y)

    def encode(self, compressed, hash160=False):
        """return the SEC bytes encoding of the public key Point"""
        # calculate the bytes
        if compressed:
            # (x,y) is very redundant. Because y^2 = x^3 + 7,
            # we can just encode x, and then y = +/- sqrt(x^3 + 7),
            # so we need one more bit to encode whether it was the + or the -
            # but because this is modular arithmetic there is no +/-, instead
            # it can be shown that one y will always be even and the other odd.
            prefix = b"\x02" if self.y % 2 == 0 else b"\x03"
            pkb = prefix + self.x.to_bytes(32, "big")
        else:
            pkb = b"\x04" + self.x.to_bytes(32, "big") + self.y.to_bytes(32, "big")
        # hash if desired
        return ripemd160(sha256(pkb)) if hash160 else pkb

    def address(self, net: str, compressed: bool) -> str:
        """return the associated bitcoin address for this public key as string"""
        # encode the public key into bytes and hash to get the payload
        pkb_hash = self.encode(compressed=compressed, hash160=True)
        # add version byte (0x00 for Main Network, or 0x6f for Test Network)
        version = {"main": b"\x00", "test": b"\x6f"}
        ver_pkb_hash = version[net] + pkb_hash
        # calculate the checksum
        checksum = sha256(sha256(ver_pkb_hash))[:4]
        # append to form the full 25-byte binary Bitcoin Address
        byte_address = ver_pkb_hash + checksum
        # finally b58 encode the result
        b58check_address = b58encode(byte_address)
        return b58check_address

from __future__ import annotations

from utils import b58encode, is_prime, ripemd160, sha256


class Curve:
    """
    Elliptic Curve over the field of integers modulo a prime.
    Points on the curve satisfy y^2 = x^3 + a*x + b (mod p), where 4*a^3 + 27*b^2 != 0 (mod p).
    """

    def __init__(self, p: int, a: int, b: int):
        assert p > 3, "p must be > 3"
        assert (4 * a**3 + 27 * b**2) % p != 0, "Curve must not be singular"
        assert is_prime(p), "p is not prime"

        self.p = p
        self.a = a
        self.b = b

    def __repr__(self):
        return f"Curve(p={self.p}, a={self.a}, b={self.b})"


class Point:
    """An integer point (x,y) on an elliptic curve"""

    def __init__(self, curve: Curve, x: int, y: int):
        if not (x is None and y is None):  # ideal point
            assert (
                y**2 % curve.p == (x**3 + curve.a * x + curve.b) % curve.p
            ), "Point is not on the curve"
        self.curve = curve
        self.x = x
        self.y = y

    @classmethod
    def from_ideal_point(cls):
        return cls(None, None, None)

    def is_ideal_point(self) -> bool:
        return self.x is None and self.y is None

    def __repr__(self):
        return f"Point({self.x}, {self.y}) - Curve: {self.curve}"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.curve == other.curve and self.x == other.x and self.y == other.y

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

        if self.is_ideal_point():
            return other
        if other.is_ideal_point():
            return self
        # handle special case of P + (-P) = 0
        if self.x == other.x and self.y != other.y:
            return Point.from_ideal_point()
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
        result = Point.from_ideal_point()
        append = self
        while k:
            if k & 1:
                result += append
            append += append
            k >>= 1
        return result

    def __mul__(self, other: int) -> Point:
        return self.__rmul__(other)


class Generator:
    """
    A generator over a curve: an initial point and the (pre-computed) order
    """

    def __init__(self, G: Point, n: int):
        self.G = G
        self.n = n


class PrivateKey:
    """
    An private key. Basically an integer.
    """

    def __init__(self, secret: int):
        self.secret = secret

    def get_public_key(self, generator_point: Point) -> PublicKey:
        """returns the public key point corresponding to the private key"""
        return PublicKey.from_point(self.secret * generator_point)


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

    def address(self, net: str, compressed: bool = True) -> str:
        """return the associated bitcoin address for this public key as string"""
        assert net in ["main", "test"], "Network must be 'main' or 'test'"
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

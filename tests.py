# using unittest to test the functions in the file
import unittest
from data_classes import Point, Curve, Generator, PublicKey
from hash_utils import ripemd160, sha256
import random

bitcoin_curve = Curve(
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a=0x0000000000000000000000000000000000000000000000000000000000000000,  # a = 0
    b=0x0000000000000000000000000000000000000000000000000000000000000007,  # b = 7
)

bitcoin_generator_point = Point(
    bitcoin_curve,
    x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

class CurveTestCase(unittest.TestCase):
    def test_curve_initialization(self):
        curve = Curve(p=17, a=2, b=2)
        self.assertEqual(curve.p, 17)
        self.assertEqual(curve.a, 2)
        self.assertEqual(curve.b, 2)

class PointTestCase(unittest.TestCase):
    def setUp(self):
        self.curve = bitcoin_curve
        self.generator = bitcoin_generator_point
        self.point1 = self.generator
        self.point2 = self.generator * 2
        self.point3 = self.generator * 3
        self.point4 = Point(self.curve, 5, 1)

    def test_addition(self):
        # Test addition of two points
        result = self.point1 + self.point2
        pass

    def test_multiplication(self):
        # Test multiplication of a point with a scalar
        result = self.point1 * 3
        pass

    def test_addition_same_as_multiplication(self):
        for P in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(P == P * 1)
            self.assertTrue(P == 1 * P)
            self.assertTrue(P + P == P * 2)
            self.assertTrue(P + P == 2 * P)
            self.assertTrue(P + P + P == P * 3)
            self.assertTrue(P + P + P == 3 * P)

    def test_point_is_on_curve(self):
        # Test that the point is on the curve
        for P in [self.point1, self.point2, self.point3]:
            self.assertTrue(P.is_on_curve())

        # Test that the point is not on the curve
        self.assertFalse(self.point4.is_on_curve())

class GeneratorTestCase(unittest.TestCase):
    def test_generator_initialization(self):
        curve = Curve(a=2, b=3, p=17)
        G = Point(x=1, y=2, curve=curve)
        n = 10  # Example value for the order of the generator point

        generator = Generator(G, n)

        self.assertEqual(generator.G, G)
        self.assertEqual(generator.n, n)


class TestPublicKey(unittest.TestCase):
    def setUp(self):
        # Create a sample Point object
        curve = Curve(a=2, b=3, p=17)
        x = 5
        y = 1
        self.point = Point(curve, x, y)
        # Create a sample PublicKey object
        self.public_key = PublicKey.from_point(self.point)

    def test_encode_compressed(self):
        # Test encoding with compressed=True
        encoded = self.public_key.encode(compressed=True)
        expected = ...
        pass


if __name__ == "__main__":
    unittest.main()

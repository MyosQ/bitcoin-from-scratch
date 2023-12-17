# using unittest to test the functions in the file
import unittest

from data_classes import Curve, Generator, Point, PrivateKey, PublicKey

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
        curve = Curve(p=17, a=1, b=1)
        self.assertEqual(curve.p, 17)
        self.assertEqual(curve.a, 1)
        self.assertEqual(curve.b, 1)

    def test_init_with_invalid_parameters(self):
        with self.assertRaisesRegex(AssertionError, "p must be > 3"):
            Curve(p=2, a=1, b=1)

        with self.assertRaisesRegex(AssertionError, "Curve must not be singular"):
            Curve(p=17, a=-3, b=2)

        with self.assertRaisesRegex(AssertionError, "p is not prime"):
            Curve(p=18, a=1, b=1)


class PointTestCase(unittest.TestCase):
    def setUp(self):
        self.curve = bitcoin_curve
        self.generator = bitcoin_generator_point
        self.point1 = self.generator
        self.point2 = self.generator * 2

    def test_addition(self):
        curve = Curve(p=17, a=-7, b=10)
        P = Point(curve, x=1, y=2)
        Q = Point(curve, x=3, y=4)
        assert P + Q == Point(curve, x=14, y=2)

    def test_addition_same_as_multiplication(self):
        for P in [self.point1, self.point2]:
            self.assertTrue(P == P * 1)
            self.assertTrue(P == 1 * P)
            self.assertTrue(P + P == P * 2)
            self.assertTrue(P + P == 2 * P)

    def test_init_with_invalid_parameters(self):
        with self.assertRaisesRegex(AssertionError, "Point is not on the curve"):
            Point(self.curve, 5, 1)


class GeneratorTestCase(unittest.TestCase):
    def test_generator_initialization(self):
        G = bitcoin_generator_point
        n = 10  # Example value for the order of the generator point
        generator = Generator(G, n)

        self.assertEqual(generator.G, G)
        self.assertEqual(generator.n, n)


class PrivateKeyTests(unittest.TestCase):
    def test_private_key_initialization(self):
        private_key = PrivateKey(123)
        assert private_key.secret == 123

    def test_get_public_key(self):
        generator_point = bitcoin_generator_point

        # Test with a trivial private key 1
        private_key = PrivateKey(1)
        public_key = private_key.get_public_key(generator_point)
        self.assertIsInstance(public_key, PublicKey)
        self.assertEqual(public_key, PublicKey.from_point(generator_point))

        # Test with a trivial private key 2
        private_key = PrivateKey(2)
        public_key = private_key.get_public_key(generator_point)
        self.assertIsInstance(public_key, PublicKey)
        self.assertEqual(public_key, PublicKey.from_point(generator_point * 2))


class TestPublicKey(unittest.TestCase):
    def test_lol_address(self):
        lol_public_key = bitcoin_generator_point
        lol_address = PublicKey.from_point(lol_public_key).address(
            net="test", compressed=True
        )
        self.assertEqual(lol_address, "mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r")


if __name__ == "__main__":
    unittest.main()

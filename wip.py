from __future__ import \
    annotations  # PEP 563: Postponed Evaluation of Annotations

import random

from data_classes import Curve, Generator, Point, PublicKey

# secp256k1 uses a = 0, b = 7, so we're dealing with the curve y^2 = x^3 + 7 (mod p)
bitcoin_curve = Curve(
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a=0x0000000000000000000000000000000000000000000000000000000000000000,  # a = 0
    b=0x0000000000000000000000000000000000000000000000000000000000000007,  # b = 7
)

G = Point(
    bitcoin_curve,
    x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    y=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

bitcoin_gen = Generator(
    G=G,
    # the order of G is known and can be mathematically derived
    n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
)

# we can verify that the generator point is indeed on the curve, i.e. y^2 = x^3 + 7 (mod p)
print("Generator IS on the curve: ", (G.y**2 - G.x**3 - 7) % bitcoin_curve.p == 0)

# some other totally random point will of course not be on the curve, _MOST_ likely

random.seed(1337)
x = random.randrange(0, bitcoin_curve.p)
y = random.randrange(0, bitcoin_curve.p)
print("Totally random point is not: ", (y**2 - x**3 - 7) % bitcoin_curve.p == 0)

secret_key = int.from_bytes(
    b"Andrej is cool :P", "big"
)  # this is how I will do it for reproducibility
assert 1 <= secret_key < bitcoin_gen.n
print(secret_key)

# if our secret key was the integer 1, then our public key would just be G:
sk = 1
pk = G
print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
print(
    "Verify the public key is on the curve: ",
    (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0,
)
# if it was 2, the public key is G + G:
sk = 2
pk = G + G
print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
print(
    "Verify the public key is on the curve: ",
    (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0,
)
# etc.:
sk = 3
pk = G + G + G
print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
print(
    "Verify the public key is on the curve: ",
    (pk.y**2 - pk.x**3 - 7) % bitcoin_curve.p == 0,
)

# "verify" correctness
print(G == 1 * G)
print(G + G == 2 * G)
print(G + G + G == 3 * G)

# efficiently calculate our actual public key!
public_key = secret_key * G
print(f"x: {public_key.x}\ny: {public_key.y}")
print(
    "Verify the public key is on the curve: ",
    (public_key.y**2 - public_key.x**3 - 7) % bitcoin_curve.p == 0,
)

# we are going to use the develop's Bitcoin parallel universe "test net" for this demo, so net='test'
address = PublicKey.from_point(public_key).address(net="test", compressed=True)
print(address)

lol_secret_key = 1
lol_public_key = lol_secret_key * G
lol_address = PublicKey.from_point(lol_public_key).address(net="test", compressed=True)
print(lol_address)

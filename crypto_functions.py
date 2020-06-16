import hashlib

from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import Crypto

#sign == bytes.fromhex(sign.hex())
def generate_hash(string):
    return hashlib.sha256(string.encode()).hexdigest()


def generate_public_private_keys():
    seed =  Crypto.Random.new().read
    private_key = RSA.generate(1024,seed)
    public_key = private_key.publickey()
    private_pem = private_key.exportKey('PEM')
    public_pem = public_key.exportKey('PEM')
    return public_pem, private_pem

def key_in_RSA_object(key):  ## Input is string
    return RSA.importKey(key)

def sign_data(data,private_key):  ## expect data in string
    signer = PKCS1_v1_5.new(private_key)
    digest = SHA256.new()
    digest.update(data.encode())
    sig = signer.sign(digest)
    return sig

def verify_sign(data,sign,public_key):
    digest = SHA256.new()
    digest.update(data.encode())
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, sign)
    return verified
import hashlib

from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256,SHA1,SHA224,SHA384,SHA512
import Crypto

#sign == bytes.fromhex(sign.hex())
# def generate_hash(string):
#     return hashlib.sha256(string.encode()).hexdigest()

def generate_hash(string,type):
    if type not in ['SHA1','SHA224','SHA256','SHA384','SHA512']:
        print("unknown type of hash")
        return
    if type == 'SHA1':
        obj = SHA1.new()
    if type == 'SHA224':
        obj = SHA224.new()
    if type == 'SHA256':
        obj = SHA256.new()
    if type == 'SHA384':
        obj = SHA384.new()
    if type == 'SHA512':
        obj = SHA512.new()
    
    obj.update(string.encode())
    return obj.hexdigest()

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

import os
import hmac
import hashlib
import struct
import codecs
import ecdsa
import binascii
from pprint import pprint
import base58
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int, generator_secp256k1
from ecdsa.numbertheory import square_root_mod_prime
from key_utils import generate_mnemonic, ENTROPY, create_seed, verify_mnemonic, zero_padding

X_PRIVATE = '0488ade4' # Version string for mainnet extended private keys
X_PUBLIC  = '0488b21e' # Version string for mainnet extended public keys
HARDENED = 0x80000000

class Key(object):

    @staticmethod
    def usingMnemonic(mnemonic="", salt="", public=False):
        "Create a Key using mnemonic"

        if mnemonic == "":
            entropy = ENTROPY
            # entropy = os.urandom()
            print("Generating new mnemonic...\n")
            mnemonic = generate_mnemonic(entropy)
            print(mnemonic,"\n")
            seed = create_seed(mnemonic, salt)
        else:
            if verify_mnemonic(mnemonic):
                seed = create_seed(mnemonic,salt)
            else:
                raise ValueError("Mnemonic is wrong")

        output = hmac.new(b'Bitcoin seed', seed, hashlib.sha512).digest()

        left, right = output[:32], output[32:]

        key = Key(secret=left, chain=right, level=0, index=b'\x00\x00\x00\x00', fingerprint=b'\x00\x00\x00\x00', public=False)
        if public:
            key.k = None
            key.public = True

        return key

    @staticmethod
    def usingSeed(self,seed):
        output = hmac.new('Bitcoin seed', seed, hashlib.sha512).digest()

        left, right = output[:32], output[32:]

        key = Key(secret=left, chain=right, level=0, index=b'\x00\x00\x00\x00', fingerprint=b'\x00\x00\x00\x00', public=False)
        if public:
            key.k = None
            key.public = True

        return key


    def __init__(self, secret, chain, level, index, fingerprint, public=False):
        self.public = public
        if public is False:
            self.k = ecdsa.SigningKey.from_string(secret, curve=SECP256k1)
            self.public_key = self.k.get_verifying_key()
        else:
            self.k = None
            self.public_key = secret

        self.chain = chain
        self.level = level
        self.index = index
        self.parent_fingerprint = fingerprint
        self.children = []

    # set public = True to get xpub
    def serialize(self, public=False, encoded=True):

        if self.public and public is False:
            raise Exception("Cannot serialize private key from public key")

        version = binascii.unhexlify(X_PUBLIC) if public else binascii.unhexlify(X_PRIVATE)
        level = self.level.to_bytes(1,'big')
        fingerprint = self.parent_fingerprint
        child = self.index
        chain = self.chain


        if self.public or public:
            data = self.get_public_key().hex()
        else:
            data = '00' + self.get_private_key().hex()

        data = binascii.unhexlify(data)

        raw = version + level + fingerprint + child + chain + data

        assert(len(data) == 33)
        assert(len(raw) == 78)

        if not encoded:
            return raw.hex()
        else:
            return base58.b58encode_check(raw)

    def child_priv(self, index):
        if index >= 0x80000000:
            data = b'\0' + self.k.to_string() + index.to_bytes(4,'big')
        else:
            k_int = string_to_int(self.k.to_string())
            point = k_int * generator_secp256k1
            compressed = self.sec(point)
            data = compressed + index.to_bytes(4,'big')

        left, right = self.hmac(data)

        left_int = string_to_int(left)
        k_int = string_to_int(self.k.to_string())
        child_k_int = (left_int + k_int) % generator_secp256k1.order()
        if (child_k_int == 0) or left_int >= generator_secp256k1.order():
            return None
        child_key = int_to_string(child_k_int)
        child_key = zero_padding(32,child_key)

        assert(len(child_key) == 32)

        key = Key(secret=child_key, chain=right, level=self.level+1, index=index.to_bytes(4,'big'), fingerprint=self.fingerprint(), public=False)
        self.children.append(key)

        return key


    def child_pub(self, index):
        if index >= 0x80000000:
            raise Exception("Cannot create hardened public key")
        data = self.get_public_key() + index.to_bytes(4,'big')
        left, right = self.hmac(data)

        left_int = string_to_int(left)
        point = left_int * generator_secp256k1 + self.public_key.pubkey.point
        res = ecdsa.VerifyingKey.from_public_point(point, curve=SECP256k1)

        key = Key(secret=res, chain=right, level=self.level+1, index=index.to_bytes(4,'big'), fingerprint=self.fingerprint(), public=True)
        self.children.append(key)

        return key

    def get_child(self, index):
        return self.child_pub(index) if self.public else self.child_priv(index)

    def get_private_key(self):
            return self.k.to_string()

    def get_public_key(self):
        '''
        SEC1 compressed
        '''
        sec = self.sec(self.public_key.pubkey.point)
        return sec

    def identifier(self):
        key = self.get_public_key()
        return hashlib.new('ripemd160', hashlib.sha256(key).digest()).digest()

    def fingerprint(self):
        return self.identifier()[:4]

    def address(self):
        vh160 = '00' + self.identifier().hex()
        vh160 = binascii.unhexlify(vh160)
        return base58.b58encode_check(vh160)

    def testnet_address(self):
        vh160 = '6F' + self.identifier().hex()
        vh160 = binascii.unhexlify(vh160)
        return base58.b58encode_check(vh160)

    def chain_code(self):
        return self.chain.hex()

    def set_public(self):
        self.k = None
        self.public = True

    def wif(self):
        if self.public:
            raise Exception("Publicly derived deterministic keys have no private half")
        raw = '80' + self.k.to_string().hex() + '01'
        raw = binascii.unhexlify(raw)
        return base58.b58encode_check(raw)


    def hmac(self, data):
        I = hmac.new(self.chain, data, hashlib.sha512).digest()
        return (I[:32], I[32:])

    def sec(self,point):
        if point.y() & 1:
            return b'\3' + zero_padding(32,int_to_string(point.x()))
        else:
            return b'\2' + zero_padding(32,int_to_string(point.x()))


    def info(self):
        wallet = {
            "pub" : self.get_public_key().hex(),
            "xpub" : self.serialize(public = True).decode(),
            "chain" : self.chain.hex(),
            "identifier" : self.identifier().hex(),
            "fingerprint" : self.fingerprint().hex(),
            "parent fingerprint" : self.parent_fingerprint.hex(),
            "level" : str(self.level),
            "children" : [],
            "address" : self.address().decode(),
            "testnet address" : self.testnet_address().decode()
        }
        if not self.public:
            wallet["xprv"] = self.serialize().decode()
            wallet["wif"] = self.wif().decode()
            wallet["priv"] = self.get_private_key()

        return wallet

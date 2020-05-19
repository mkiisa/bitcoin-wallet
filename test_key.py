
import unittest
from key_utils import create_seed
from key import Key
import binascii
import base58

MNEMONIC = "index person garbage fiscal maid present boost stick broken edit erupt wrong"
key = Key.usingMnemonic(MNEMONIC)
public_key = Key.usingMnemonic(MNEMONIC, public = True)
wallet = key.info()

class TestingKey(unittest.TestCase):

    def test_seed(self):
        self.assertEqual(create_seed(MNEMONIC).hex(),'5634cc89559725a5178b1b4b0ea0738eb1b02371ef0c383eb2833215072f02963f7b9f9ba10e2e934f4278c356eb1573666b44aa30e8d39f848438d2c89d7c79')

    def test_serialize(self):
        self.assertEqual(key.serialize(public = False), b'xprv9s21ZrQH143K3dKuQw9RTE9DBCsu558kuhWx5WfPc183HLM57cea4nbD4xsoUMPeU4i8VXWfpvZtJrgxRV1pLcwi7JrvYy1pmKUYv5rvm9n')
        self.assertEqual(key.serialize(public = True), b'xpub661MyMwAqRbcG7QNWxgRpN5wjEiPUXrcGvSYsu51ALf2A8gDf9xpcaugvEXLCdGkiPwskTQVkkwT7jrs313vqTkAv6k95Cbzx78DU2AxtjN')

    def test_wif(self):
        self.assertEqual(wallet['wif'], 'KzWdqzFcjy4UDeDxSVaow2MeCNdyESemaTWEy3vm3SuEAHhFKzrU')

    def test_child_der(self):
        priv = key.child_priv(0).info()
        pub = key.child_pub(0).info()
        harden = key.child_priv(0x80000000).info()
        self.assertEqual(priv["xprv"], 'xprv9vZmtyeDWErFEGwyUUvbCKF4qfX7Sm6y6GgAFFXScncxRoWSE7gvYKTXJrzBu5F5s4DcxRCjngXttq9TWpACUrNLf8QRsHURzDr5EEvetJ8')
        self.assertEqual(priv["xpub"],'xpub69Z8JVB7LcQYSm2SaWTbZTBoPhMbrDppTVbm3dw4B89wJbqamf1B67n1AA2vcAYbKT94JfaCQSf5Eq5GviYAf8Vsvyncbk5Tf7etfpgVRC3')
        self.assertEqual(pub["xpub"], 'xpub69Z8JVB7LcQYSm2SaWTbZTBoPhMbrDppTVbm3dw4B89wJbqamf1B67n1AA2vcAYbKT94JfaCQSf5Eq5GviYAf8Vsvyncbk5Tf7etfpgVRC3')
        self.assertEqual(harden["xprv"], 'xprv9vZmtyeMquPDSRLMM4ffp3zKx5JN5eJ8Qw522NbVb8Mx79g5KGSXtJJ6d3x6TEPDPBqvdhdMDPC9QgutU18ombDEKDjhBJK9KonGsJNPiCY')
        self.assertEqual(harden["xpub"], 'xpub69Z8JVBFgGwWeuQpT6CgBBw4W78rV71yn9zcpm179Ttvyx1DroknS6caUKYQf6R3jPRj8AeCQkV6vHuqPbjYoHVDukJg4z3P8nKtF8eGB3C')


    def test_get_private_key(self):
        self.assertEqual(wallet["priv"], base58.b58decode_check("KzWdqzFcjy4UDeDxSVaow2MeCNdyESemaTWEy3vm3SuEAHhFKzrU")[1:-1])

    def test_get_public_key(self):
        self.assertEqual(wallet["pub"], "02b36cb9043721c78030a490f20c54ffdbfa3fe1103c92eb38b6e34060aab9278a")

    def test_identifier(self):
        self.assertEqual(wallet["identifier"],"e2a9ba3fcf503614570629b7cdd95f532283d4d0")

    def test_fingerprint(self):
        self.assertEqual(wallet["fingerprint"], 'e2a9ba3f')

    def test_address(self):
        self.assertEqual(wallet["address"], '1MfV3EKUd6eAa1iRhV2R1hkyNTdWKNhZU5')


if __name__ == '__main__':
    unittest.main()


import unittest
from pprint import pprint
from wallet import Wallet

# this wallet as certain amount of coins to do the unittests
TEST_WORDS = "index person garbage fiscal maid present boost stick broken edit erupt wrong"


wallet = Wallet(mnemonic=TEST_WORDS)
wallet.new_account()

empty_wallet = Wallet()

class TestingWallet(unittest.TestCase):

    def test_get_balance(self):
        bal = wallet.balance()
        acc0 = wallet.account_balance(0)
        acc1 = wallet.account_balance(1)
        empty_bal = empty_wallet.balance()

        self.assertEqual(bal,5584)
        self.assertEqual(acc0,5584)
        self.assertEqual(acc1,0)
        self.assertRaises(ValueError,wallet.account_balance,2)

        self.assertEqual(empty_bal,0)
        self.assertRaises(ValueError,empty_wallet.account_balance,0)

    def test_new(self):
        curr_account = len(wallet.hierarchy) - 1
        curr_addr = len(wallet.hierarchy.get(curr_account))
        new_acc = wallet.new_account()
        new_addr = wallet.new_address(curr_account)

        self.assertEqual(new_acc,curr_account + 1)
        self.assertEqual(new_addr,wallet.get_address(curr_account,0,curr_addr + 1))


    def test_create_tx(self):
        addr = "1PUPjAioCDRroNQrpHRJZXALtYSutJJZaZ"
        correct_tx = "0100000001e3cb9fdcbf2f93fa98c1f1aec435f4dcafe25ac26e9eb7b7f381606efe05b069000000008a47304402207bf427e845e9ce4035b31525230a21c29119a8ad89ee7bfe5f04f269bdfb1bcb0220395f371af1fcd450b9917d1a6eebe014a768a91d2cf0d22940311f95d8d424120141042ee7ff0a9a14ac9cd644d6c49176d53f4c7c726a617eda76ef470371f97641a13d688b7522298a5cd8f26b2d18ffe16a827b1ec13b657e75bf5dd9a239f0886dffffffff02ae080000000000001976a914f680f8436917687d39df9d485c38b1081b22b51888ac5a0c0000000000001976a914da343fe150b958bee34f9d5a5a26cddba6b06c3f88ac00000000"
        tx = wallet.create_tx(0, addr, 2222,fee = 200)

        self.assertEqual(tx,correct_tx)
        self.assertRaises(Exception,wallet.create_tx,1, addr, 2222,fee = 200)
        self.assertRaises(Exception,wallet.create_tx,1, addr, 0,fee = 0)
        self.assertRaises(Exception,wallet.create_tx,10, addr, 2,fee = 2)
        self.assertRaises(Exception,wallet.create_tx,1, addr, -1,fee = -1)

    def test_from_path(self):

        self.assertEqual(wallet.from_path("m/0/0/0/0").info()['xprv'],"xprvA1h4q3C7Hd6d7aHNjrGfreFYckR5fSw3MJbzL7dd4fiSAfyTaYLca9yXXo86Wj346ZUD4t1kkedN7TfSeM8gkCrUTVE8ggwrgzumxdm764K")
        self.assertEqual(wallet.from_path("m/0'/0'/0/0").info()['xprv'],"xprvA23GvfyV4QhPAkxBPLxQhadAT9JGxp35pfRdobM9FsDzYMSvDWPJi3gExhBsKLErqHB7SpHDEpLXCxkCnqFTNSm7xRzEqq5Zey3DJQaqGJd")
        self.assertEqual(wallet.from_path("m/5/0'/3").info()['xprv'],"xprv9yNicmgSUxD6JkMisQ3ZcKYUH74eoPhaQgddRUJBhLoqWx8P4aMFdyESfbxBuTzWdT9Mr9qgoFyi1qRp7GiqBv6kKvJBneV1aWYwzoAj2qE")
        self.assertEqual(wallet.from_path("m/44'/0'/0'/0/1").info()['xprv'],"xprvA4HfpA3ovPKBRxywCeANYnvQcgZn9xgqQG8aJivU4QBPhfaCMk1bo8FQpsDjtw5jsSWJ4gBxoVrrZed3F6mfkSc2tv2Qjg3fYD9KLwmJuDV")
        self.assertRaises(Exception, wallet.from_path,"M/0'/0/0/0")


    def test_get_utxo(self):
        utxo = wallet.get_utxo(0,2000)
        self.assertEqual(utxo[0]['value'], 5584)
        self.assertEqual(utxo[0]['key_info'], (0, 0, 1))
        self.assertEqual(utxo[0]['output'], "69b005fe6e6081f3b7b79e6ec25ae2afdcf435c4aef1c198fa932fbfdc9fcbe3:0")

        self.assertRaises(ValueError,wallet.get_utxo,1,10000)
        self.assertRaises(ValueError,wallet.get_utxo,1,-1)




if __name__ == '__main__':
    unittest.main()

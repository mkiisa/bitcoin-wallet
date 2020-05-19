
import hashlib
import base58
import time
import requests
import binascii
from pprint import pprint
from key import Key
from bitcoin import mktx, sign, serialize, pushtx, history, unspent
from cryptos import Bitcoin

from key_utils import generate_mnemonic, verify_mnemonic

ADDRESS_CAP = 3

def btc_to_satoshi(b):
    return b * 100000000

class Wallet:
    def __init__(self, mnemonic=""):
        '''
        create master bip32 key object either with seed or generate new mnemonics
        if existing seed, do account/address search (bip44)
        set up branch records according to BIP 44 for Bitcoin
        '''
        self.master = Key.usingMnemonic(mnemonic=mnemonic)

        # key = account_num, value = {address_num : address}  -- only issued addresses and accounts are saved
        self.hierarchy = {}
        self.free_account = 0
        self.change_hierarchy = {}
        self.btc = Bitcoin()

        if mnemonic != "":
            self.initialize_wallet()


    def create_tx(self,from_account, to_addr, amount,fee = 0):
        '''
        Create a serialized transaction from funds under 'from_account'

        returns signed serialized tx
        '''
        spendables = self.get_utxo(from_account, amount + fee)
        if not spendables:
            raise Exception("Account is empty or amount to send is 0")
        assert(fee >= 0 and amount > 0)

        keys = []
        total = 0
        for sp in spendables:
            keys.append(self.get_key(sp['key_info'][0],sp['key_info'][1],sp['key_info'][2]))
            total += sp['value']
            del sp['key_info']

        change_addr = self.new_address(from_account,change=1)
        payables = [{'value' : amount,'address' : to_addr},{'value' : total - fee - amount,'address' : change_addr}]

        tx = mktx(spendables,payables)
        for i,key in enumerate(keys):
            priv = key.get_private_key().hex()
            tx = sign(tx,i,priv)

        return tx


    def send(self,from_account, to_addr, amount,fee = 0):
        ''' This method sends the transaction from create_tx to the mainnet'''
        tx = self.create_tx(from_account, to_addr, amount, fee)
        res = pushtx(binascii.unhexlify(tx))
        return res


    def balance(self, verbose = True):
        '''
        prints out all accounts' balances as a dictionary

        returns all accounts balances summed together
        '''
        res = {}
        total = 0
        for i in self.hierarchy:
            balance = self.chain_balance(i,False)
            total += balance
            res[i] = balance

        for i in self.change_hierarchy:
            balance = self.chain_balance(i,True)
            total += balance
            if res.get(i):
                res[i] += balance
            else:
                res[i] = balance

        if verbose:
            print("Wallet balance...")
            pprint(res)

        return total


    def account_balance(self,acc_num):
        '''
        returns balance on account
        '''

        if self.hierarchy.get(acc_num) is None and self.change_hierarchy.get(acc_num) is None:
            raise ValueError("Account %i hasn't been created" % acc_num)
        elif self.hierarchy.get(acc_num) is None:
            raise Exception("account in internal chain cannot exist if it doesn't exist on external chain")
        elif self.change_hierarchy.get(acc_num) is None:
            total = self.chain_balance(acc_num,False,verbose = False)
        else:
            total = self.chain_balance(acc_num,False,verbose = False) + self.chain_balance(acc_num,True,verbose = False)
        return total


    def chain_balance(self,acc_num, change,verbose = False):
        '''
        inner method
        params
            acc_num = account number
            change = 1 or 0
            verbose = prints out balances under each address on hierarchy

        returns : balance on internal or external chain
        '''
        if change:
            if verbose:
                print("Scanning internal chain : account %i ..." % acc_num)
            if self.change_hierarchy.get(acc_num) is None:
                raise Exception("Account number %i hasn't been created yet." % acc_num)
            int_entry = self.change_hierarchy[acc_num]
            balance, entry = self.balance_helper(int_entry)
            if verbose:
                print("\nInternal chain balance ...\n")
                pprint(entry)
        else:
            if verbose:
                print("Scanning external chain : account %i ..." % acc_num)
            if self.hierarchy.get(acc_num) is None:
                raise Exception("Account number %i hasn't been created yet." % acc_num)
            ext_entry = self.hierarchy[acc_num]
            balance, entry = self.balance_helper(ext_entry)
            if verbose:
                print("\nExternal chain balance ...\n")
                pprint(entry)

        return balance


    def balance_helper(self,entry):
        '''inner method'''
        total = 0
        d = {}
        for i in entry:
            value = self.btc.history(entry[i])['final_balance']
            d[i] = value
            total += value
        return total, d


    def get_key(self,account,change,addr):
        path = self.build_addr_path(account,change,addr)
        return self.from_path(path)


    def get_address(self,account,change,addr):
        return self.get_key(account,change,addr).address().decode()


    def get_utxo(self,account_num,amount):
        '''
        Get all available UTXO from 'account_num' that exceeds 'amount'

        returns = list of spendable outputs
        '''

        if self.hierarchy.get(account_num) is None:
            raise ValueError("Account : %i hasn't been created yet" % account_num)
        if amount <= 0:
            raise ValueError("'amount' has negative or zero value")

        # getting change first
        int_utxo, int_val = self.get_utxo_helper(account_num,1,amount)
        if int_val >= amount:
            return int_utxo

        ext_utxo, ext_val = self.get_utxo_helper(account_num,0,amount)

        sum = (ext_val + int_val)
        if sum < amount:
            raise ValueError("Account : %i doesn't have enough money. Balance = %i required = %i" %(account_num, ext_val + int_val, amount))

        return ext_utxo + int_utxo



    def get_utxo_helper(self,account_num,change,value):
        '''
        inner method
        param:
            change = either 0 or 1 depending whether browsing internal or external chain (BIP-44)
            value = amount of utxo to find
            account_num = account number

        get spendables for sending money
        '''
        # check if account exists
        collected = 0 # amount of utxo saved in spendables in satoshi
        spendables = []

        if change == 0:
            account_entry = self.hierarchy.get(account_num)
            if account_entry is None:
                return spendables, collected
        elif change == 1:
            account_entry = self.change_hierarchy.get(account_num)
            if account_entry is None:
                return spendables, collected
        else:
            raise Exception("Wrong 'change' parameter in get_spendables_helper().")


        for addr_num in account_entry:
            address = account_entry[addr_num]
            addr_utxo = self.btc.unspent(address)
            for output in addr_utxo:
                if collected >= value:
                    return spendables, collected
                collected += output["value"]
                output["key_info"] = (account_num,change,addr_num)
                spendables.append(output)

        return spendables, collected


    def new_account(self):
        '''
        create a new account
        returns the number of the account
        '''

        account = self.free_account
        self.hierarchy[account] = {}
        self.change_hierarchy[account] = {}
        self.free_account += 1
        return account



    def new_address(self, account_num, change=0):
        '''
        create an account address for receiving money
        '''
        if self.hierarchy.get(account_num) is None and change == 0:
            raise Exception("Account number %i does not exist in the record" % account_num)
        if self.change_hierarchy.get(account_num) is None and change == 1:
            raise Exception("Account number %i does not exist in the change_record" % account_num)


        if change == 1:
            account = self.change_hierarchy[account_num]
            new_addr_num = len(self.change_hierarchy[account_num].keys()) + 1
            new_addr = self.get_address(account_num,change,new_addr_num)
            self.change_hierarchy[account_num][new_addr_num] = new_addr
        elif change == 0:
            account = self.hierarchy[account_num]
            new_addr_num = len(self.hierarchy[account_num].keys()) + 1
            new_addr = self.get_address(account_num,change,new_addr_num)
            self.hierarchy[account_num][new_addr_num] = new_addr
        else:
            raise Exception("Wrong value for 'change' parameter")

        return new_addr


    def build_addr_path(self,account,change,addr):
        return "m/44'/0'" + "/" + str(account) + "'/" + str(change) + "/" + str(addr)


    def from_path(self,path):
        '''
        inner method
        Create a bip32 key from path e.g "m/0'/23/3/2"

        returns bip32 key object from key.py
        '''
        path_list = path.split('/')

        if path_list[0] == 'm':
            parent = self.master
        elif path_list[0] == 'M':
            parent = self.master_pub
        else:
            raise ValueError("Error in the path - must start with M or m: %s", path)

        for i,index in enumerate(path_list[1:]):

            if "'" in index:
                if path_list[0] == 'M':
                    raise Exception("Cannot derive a hardened key from a public master key")
                index = index[:-1]
                index = int(index) + 2147483648
            else:
                index = int(index)
            parent = parent.get_child(index)

        return parent



    def initialize_wallet(self):
        '''
        initialize self.hierarchy
        it is called when user creates the object with a mnemonic
        '''
        account = 0
        while True:
            free_address = self.init_addresses(account)
            if free_address == 0:
                self.free_account = account
                print("\nWallet Initialized")
                self.info()
                return
            account += 1



    def init_addresses(self, account_num):
        '''
        find first address under account that has no transaction history
        iterate through 20 addresses from last one with tx history (BIP 44)
        this constant is set to 3 in this instance to save time

        returns free address under this account number
        '''

        print("Initializing addresses for account : %i ..." % account_num)
        addr_count = 0
        last_free = 0
        internal = {}
        external = {}
        flag = True

        while True:
            external[addr_count] = self.get_address(account_num,0,addr_count)
            internal[addr_count] = self.get_address(account_num,1,addr_count)
            tx_history = history(external[addr_count])

            if len(tx_history) == 0 and flag:
                last_free = addr_count
                flag = False

            if len(tx_history) != 0:
                flag = True

            if (addr_count - last_free) == ADDRESS_CAP and not flag:
                if last_free != 0:
                    self.hierarchy[account_num] = {k: external[k] for k in range(0,last_free)}
                    self.change_hierarchy[account_num] = {k: internal[k] for k in range(0,last_free)}
                return last_free

            addr_count += 1


    def info(self):
        pprint(self.hierarchy)

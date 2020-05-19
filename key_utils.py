
import os
import hashlib
import unicodedata
import sys
import binascii

ENTROPY = '0c1e24e5917779d297e14d45f14e1a1a'
# BIP 39

def generate_mnemonic(entropy):
    '''
    create mnemonic from entropy
    '''
    h = hashlib.sha256(binascii.unhexlify(entropy)).hexdigest()

    binary = bin(int('1' + entropy, base = 16))[3:]
    h_binary = bin(int('1' + h, base = 16))[3:]
    checksum = h_binary[:len(binary)//32]
    value = binary + checksum

    ln_nums = [int(value[11*i:(i+1)*11],2) for i in range(0,len(value)//11)]
    mnemonic, words = [],[]

    with open('wordlist.txt','r') as f:
        for ln in f:
            words.append(ln[:-1])

    for i in ln_nums:
        mnemonic.append(words[i])
    return " ".join(mnemonic)


def create_seed(mnemonic,salt=""):
    '''
    create seed from mnemonic (should be outside)
    '''

    unicodedata.normalize("NFKD", salt)
    unicodedata.normalize("NFKD", mnemonic)
    salt = "mnemonic" + salt
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt.encode('utf-8'), 2048)
    return seed


def verify_mnemonic(mnemonic):
    wordlist = []
    with open('wordlist.txt','r') as f:
        for ln in f:
            wordlist.append(ln[:-1])

    mnemonic_list = mnemonic.split(" ")
    for word in mnemonic_list:
        if word not in wordlist:
            return False
    if len(mnemonic_list) < 12:
        print("Mnemonic must be longer than 12 words")
        return False
    return True


# other utils
def zero_padding(ensure_len,bytes):
    curr = len(bytes)
    diff = (ensure_len - curr)
    if diff < 0:
        raise ValueError("Bytes is longer than the ensure_len value")
    return diff * b'\x00' + bytes

if __name__ == '__main__':
    m = generate_mnemonic(ENTROPY)
    seed_no_passphrase = create_seed(m,"")
    seed_passphrase = create_seed(m,"SuperDuperSecret")
    assert(seed_passphrase.hex() == '3b5df16df2157104cfdd22830162a5e170c0161653e3afe6c88defeefb0818c793dbb28ab3ab091897d0715861dc8a18358f80b79d49acf64142ae57037d1d54')
    assert(seed_no_passphrase.hex() == '5b56c417303faa3fcba7e57400e120a0ca83ec5a4fc9ffba757fbe63fbd77a89a1a3be4c67196f57c39a88b76373733891bfaba16ed27a813ceed498804c0570')
    assert(verify_mnemonic(m))
    assert(not verify_mnemonic("army van defense carry jealous true garbage claim echo media make"))
    assert(not verify_mnemonic("army peter defense carry jealous true garbage claim echo media make crunch"))

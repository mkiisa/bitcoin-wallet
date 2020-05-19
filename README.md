
### Setup

It uses pipenv virtual environment to manage the packages and version control.
https://pypi.org/project/pipenv/

To install : `pip install pipenv`
To run : `pipenv shell`

In addition to that I used some utilities from this repo https://github.com/wizardofozzie/pybitcointools.
To set it up I entered
`git clone https://github.com/wizardofozzie/pybitcointools.git`
`python setup.py install`

### Usage

This repository contains of two parts, the key class in `key.py` and wallet class in `wallet.py`

Key represents a node in HD Wallet and all its attributes can be called through the class. It derives children keys that are also Key objects.

```
>>> k = Key.usingMnemonic()
Generating new mnemonic...

army van defense carry jealous true garbage claim echo media make crunch

>>> pprint(k.info())
{'address': '1HEyW2af1NttCX2eAwRkWBMrUrFRGzKLRW',
 'chain': 'b70d675323c40ec461e0a6af603b1f135fb2af9ae753eeff18922732a73b0f05',
 'children': [],
 'fingerprint': 'b2269592',
 'identifier': 'b22695921bab9dffb5bda2f4e5167c4b12c3b327',
 'level': '0',
 'parent fingerprint': '00000000',
 'priv': b'\xb2\xa0\xd5v\xb8(\xb57h\x8bV\x1f,\xfa\x8d\xac6\x02\xd5L'
         b'b\xbd\xe6\x19\xadS1\xe6\xc25\xee&',
 'pub': '03ca72b45eede592f059b7eaf3da13eb7d8d15aa472b6f79f74820bb22ff596186',
 'testnet address': 'mwkvo5fdpQL8ydWFtWQ8L6aBLqr8AUnS9A',
 'wif': 'L3CwXLuc2YahhutJUGgt9Qezp3rrFk7Ji7JnvzyZHb8L3osuzg2M',
 'xprv': 'xprv9s21ZrQH143K3t4UZrNgeA3w861fwjYLaGwmPtQyPMmzshV2owVpfBSd2Q7YsHZ9j6i6ddYjb5PLtUdMZn8LhvuCVhGcQntq5rn7JVMqnie',
 'xpub': 'xpub661MyMwAqRbcGN8wfsuh1Hzfg7rAMCGBwVsNCGpawhJykVpBMUp5Cym6shGYvy5RwATVHgF4vfEqvLFHQeccQtSQcVDvHhhaNB1iFF1gW8e'}
>>> k.serialize()
b'xprv9s21ZrQH143K3t4UZrNgeA3w861fwjYLaGwmPtQyPMmzshV2owVpfBSd2Q7YsHZ9j6i6ddYjb5PLtUdMZn8LhvuCVhGcQntq5rn7JVMqnie'
>>> c1 = k.get_child(1) # defaults to private key
>>> pprint(c1.info())
{'address': '15JDfq3C5nbnNBfM9vvwgiJh3jMDiofZqj',
 'chain': '9769baa2bcc6fe35e50e6dada7d65ec19c7686302cca6b351f69bcb5a5e29a56',
 'children': [],
 'fingerprint': '2f222681',
 'identifier': '2f22268162b764acbebfad5a5bd5d19b11ad800a',
 'level': '1',
 'parent fingerprint': 'b2269592',
 'priv': b'\x9bO\x98+\xe6\xb8\xdb\r\x8e\xa1I\x7f}n4\x1ai\xe7 8IG\xaf!'
         b'\x81\xfc8\x9f\x81\xcc\xe4\xb4',
 'pub': '03c57c777b7fe226dd67a7cad17ebabc0e363522ef150480b9bafc7ea464fe823c',
 'testnet address': 'mjpAxt8Atp339J8xsVuKWdX1uiwvg7ZPBx',
 'wif': 'L2Rcd8ksqLYSLCWobcNnKKEW7TTUYaUWg1cfj7nEmFunpaxTonNR',
 'xprv': 'xprv9vD6P73Kk5gLhLpohZdrSh5qn4g5kgzPoVp87ZnWrgx19YyZVEnFwpFQN2myQKXVDvXKJFQBHaaqLe4PnoxoonXxUbCzaf2A4t11CFNF75b',
 'xpub': 'xpub69CSncaDaTEdupuGobAroq2aL6WaA9iFAijiuxC8R2Uz2MJi2n6WVcZtDL54LEB6cvEkmB4SA1mUq5wbMy6TSAowmUmBjS6FFKE4gdNpCc2'}
>>> c2 = k.child_priv(0)
>>> c3 = k.child_pub(0)
>>> pprint(c3.info())
{'address': '17xkLKLunoVAUxho7EfpD24kE6tRKJjQJQ',
 'chain': 'a74b758d3dc442f8620a2438f56629e62a743a4b4fe1ad02166185bf290b56d1',
 'children': [],
 'fingerprint': '4c5bce21',
 'identifier': '4c5bce219d44927304b727605fd01d305628880b',
 'level': '1',
 'parent fingerprint': 'b2269592',
 'pub': '0261eb369da972add92ed21fd3d049689700c9a84582181a6ec286ee3f7b5cbc81',
 'testnet address': 'mnUhdNRtbpvRG5BQpoeC2wH566V8E9WhPM',
 'xpub': 'xpub69CSncaDaTEdsSFDEqX7aALRZY78zfBwxQGEYkb6E8zaXJaRYCFVDvGRJT3ePQ1SZhrxVNKuYzAgmJBqKm24TThHbmpvcWTLSEq9HmAMty1'}
```

#### Wallet objects function as described in BIP-32, BIP-39, BIP-44 specificaltions


```
>>> w = Wallet(mnemonic = "index person garbage fiscal maid present boost stick broken edit erupt wrong")
Initializing addresses for account : 0 ...
Initializing addresses for account : 1 ...

Wallet Initialized
{0: {0: '1PUPjAioCDRroNQrpHRJZXALtYSutJJZaZ',
     1: '1NYPqUQiom8FXy58UFWLHW5ZwiCPBAxR5i'}}
>>> acc0 = w.new_account()
>>> acc0
1
>>> addr0 = w.new_address(acc0)
>>> addr01 = w.new_address(acc0)
>>> w.hierarchy
{0: {0: '1PUPjAioCDRroNQrpHRJZXALtYSutJJZaZ', 1: '1NYPqUQiom8FXy58UFWLHW5ZwiCPBAxR5i'}, 1: {1: '1Lo8z7v94i8Goz3pKbrKowgmMtnKP9a6r5', 2: '187AaQmziybrAc5q8mMbJoabN72v4RivAJ'}}
>>> w.balance()
Wallet balance...
{0: 5584, 1: 0}
5584
>>>
>>> w.account_balance(acc0)
Account 1 balance is : 0
0
>>> utxo = w.get_utxo(0,2220)
>>> utxo
[{'output': '69b005fe6e6081f3b7b79e6ec25ae2afdcf435c4aef1c198fa932fbfdc9fcbe3:0', 'value': 5584, 'key_info': (0, 0, 1)}]
>>> tx = w.create_tx(0, addr0, 1,fee = 1)
>>> tx
'0100000001e3cb9fdcbf2f93fa98c1f1aec435f4dcafe25ac26e9eb7b7f381606efe05b069000000008b483045022100abbaed2588ff41f2b847618edfe6b75527f2b71854095854fa6e8ed4be9364c7022048382417da5a88b3d56d10b55df0430352f937650f9a3a4ad92a2c88f36927770141042ee7ff0a9a14ac9cd644d6c49176d53f4c7c726a617eda76ef470371f97641a13d688b7522298a5cd8f26b2d18ffe16a827b1ec13b657e75bf5dd9a239f0886dffffffff0201000000000000001976a914d92430847d04cbd22f667956817862c5a64a5dfc88acce150000000000001976a914da343fe150b958bee34f9d5a5a26cddba6b06c3f88ac00000000'

```


### Testing

Both classes have the unittests in respective files
`test_key.py` and `test_wallet.py`

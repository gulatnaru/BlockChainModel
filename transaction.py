from bitcoin import *
from Crypto.Hash import SHA256
import copy

class TxIn:
    def __init__(self):
        self.hash = ''      # 사용할 UTXO가 포함된 트랜잭션 해쉬 (Tx_id)
        self.n = 1        #위 트랜잭션 중에서 몇번째 UTXO인지
        self.address = ''   #위 UTXO의 수신주소 (공개키 해쉬.encode)
        self.value = 0     #위 UTXO의 잔액
        self.sign = ''      #서명
        self.pubk = ''      #사용자의 공개키
        self.pubk_hs = ''

class TxOut:
    def __init__(self):
        self.to = '' #받는놈 주소
        self.value = '' #금액

class Transaction:
    def __init__(self):
        self.vin_size = 0
        self.vout_size = 0
        self.inputs = []
        self.outputs = []
        self.hash = None

    def __str__(self):
        return json.dumps(self, default=self.dict_s, sort_keys = True)

    def dict_s(self, n):
        temp = copy.deepcopy(n.__dict__)
        if 'hash' in temp:
            del temp['hash']
        return temp

    def gen_hash(self):
        # self.__dict__.pop('hash')
        self.hash = hashlib.sha256(str(self).encode()).hexdigest()

    def gen_sign(self, privk):
        for input in self.inputs:
            input.pubk = privtopub(privk)
            input.pubk_hs = sha256(input.pubk)
            input.sign = ecdsa_sign(self.input.__dict__, privk)

    #public key, sign 검증
    def validate_chk(self):
        err_hash = []
        i=0
        for input in self.inputs:
            if sha256(input.pubk.encode()) == input.pubk_hs:
                print('public key hash ok')
            else:
                print('public key hacking!!!')
                raise Exception
            # sign 검증
            if ecdsa_verify(str(self.input.__dict__), input.sign, input.pubk):
                print('sign OK!')
            else:
                print('sign hacking!!')
                raise Exception

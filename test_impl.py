from backup import transaction as transac
from bitcoin import *


#1. 트랜잭션 검증
#2. 검증성공 -> Mempool(트랜잭션 대기공간)에 저장 (거래는 성사X. 0컨펌 상태)
#3. 0컨펌상태 트랜잭션이 블록에 담기는 순간 1컨펌으로 변경되고 Mempool에서 삭제됨.
class App:
    def __init__(self):
        self.in_data = transac.TxIn()
        self.out_data = transac.TxOut()
        self.tran = transac.Transaction()
        self.priv = sha256('my')
        self.pubk = privtopub(self.priv)

    def input(self):
        #genesis transaction 의 최초 key값 'my'라고 임의 설정
        # input
        ##위 UTXO의 수신주소 (공개키 해쉬)
        self.in_data.address = pubtoaddr(self.pubk) #인코딩
        self.in_data.n = '1'
        self.in_data.value = '2'
        self.in_data.pubk = self.pubk
        self.in_data.pubk_hs = sha256(self.pubk.encode())

    def output(self):
        #output
        self.out_data.value = None
        self.out_data.to = None

    def transaction(self):
        #transaction
        self.tran.inputs.append(self.in_data)
        self.tran.vin_size = len(self.tran.inputs)

        # self.tran.outputs.append(self.out_Data)
        # self.tran.vout_size = len(self.tran.outputs)

        self.in_data.hash = self.tran.gen_hash()
        self.tran.gen_sign(self.priv)
        self.tran.validate_chk()

    def print(self):
        print("######### print ###########")
        print("public key : " + self.in_data.pubk)
        print("address : "+self.in_data.address)
        print("n : " + str(self.in_data.n))
        print("value : " + str(self.in_data.value))
        print("hash : "+self.in_data.hash)
        print("sign : "+self.in_data.sign)
        print("############################")

app = App()
app.input()
app.print()
app.transaction()
app.print()


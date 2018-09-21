
from block import Block
import threading
import transaction as tr
from bitcoin import *

class Core(threading.Thread):
    def __init__(self):
        self.chain = []
        self.mempoolTrans = []
        self.block = None
        self.minerAddr = '1NSCxgvbDBHwtbVsiMZT11N577tBxWNPRZ'

    def mining(self):
        # while True :
        print('================ 블록생성 START ================')
        self.block = Block()
        self.block_setting()    # 블록값 세팅 (리워드 트랜잭션, 이전블록해시, 메모리풀 트랜잭션 이동, 머클루트)
        print('블록 데이터 : ', self.block.__dict__)
        self.chain.append(self.block)
        print('block setting의 트랜잭션 수', len(self.block.transactions))
        print('================ 블록생성 END ================')
                # time.sleep(3)

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys = True) #문자열임. 정렬

    def block_setting(self):
        self.rewardTran()
        if len(self.chain) > 0 :
            print('이전블록 해시값:', self.chain[len(self.chain) - 1].hash)
            self.block.prev_hash = self.chain[len(self.chain)-1].hash
        # self.block.mrkl_root = self.block.gen_mrkl_root()
        self.block.add_transaction(self.mempoolTrans)
        self.mempoolTrans = []
        self.block.gen_hash()   #채굴 및 hash생성

    #reward transaction
    def rewardTran(self):
        print('########## Reward Transaction ###########')
        rewardTran = tr.Transaction()
        out_data = tr.TxOut()
        out_data.value = 50
        out_data.to = self.minerAddr
        rewardTran.outputs.append(out_data)
        rewardTran.vout_size = len(rewardTran.outputs)
        rewardTran.gen_hash()
        self.mempoolTrans.append(rewardTran)

class Wallet:
    def __init__(self,core):
        self.core = core
        self.tr_input = tr.TxIn()
        self.tr_output = None

    #mempool에 트랜잭션 추가
    def add_mempool(self, tran):
        self.core.mempoolTrans.append(tran)

    #utxo찾기
    def utxo(self, my_address):
        print('# --------1.utxo 찾기 시작~!---------- #')
        my_utxo = []
        for block in self.core.chain:
            for transaction in block.transactions:
                for tr_out in transaction.outputs:
                    if tr_out.to == my_address:
                        my_utxo.append(transaction)

            for transaction in block.transactions:
                for tr_in in transaction.inputs:
                    for tran in my_utxo:
                        for tr_out in tran.outputs:
                            if tr_out.to == my_address:
                                if tr_in == tr_out:
                                    my_utxo.remove(tran)
        return my_utxo

    def send(self, my_addr, reciever_addr, coin):
        new_tran = tr.Transaction()
        utxos = self.utxo(my_addr)
        balance = 0
        #input setting
        for utxo in utxos:
            for output in utxo.outputs:
                if output.to == my_addr:
                    new_tran.inputs.append(self.inputSetting(utxo.hash, output.to, output.value))
                    balance += output.value
        #output setting
        if coin > balance:
            raise Exception
        if coin == balance:
            new_tran.outputs.append(self.outputSetting(reciever_addr, coin))
        else:
            new_tran.outputs.append(self.outputSetting(reciever_addr, coin))
            new_tran.outputs.append(self.outputSetting(my_addr, balance-coin))
        self.add_mempool(new_tran)

    def inputSetting(self, hash, address, value):
        input_tran = tr.TxIn()
        input_tran.hash = hash
        input_tran.address = address
        input_tran.n += 1
        input_tran.value = value
        return input_tran

    def outputSetting(self, to, value):
        output_tran = tr.TxOut()
        output_tran.to = to
        output_tran.value = value
        return output_tran

    def search_balance(self, my_addr):
        utxos = self.utxo(my_addr)
        balance = 0
        for utxo in utxos:
            for output in utxo.outputs:
                if output.to == my_addr:
                    balance += output.value
        return balance

class App:
    def __init__(self):
        self.key = input('키 값을 입력하세요 : ')
        self.privk = sha256(self.key)
        self.pubk = privtopub(self.privk)
        print('내 publick key : ', self.pubk)
        self.pubk_hs = sha256(self.pubk)
        print('내 publick key hash : ', self.pubk_hs)
        self.address = pubtoaddr(self.pubk)
        print('내 address : ', self.address)

        self.core = Core()
        self.wallet = Wallet(self.core)

    def start(self):
        # t1 = threading.Thread(target=self.core.mining())
        # t1.start()
        # t2 = threading.Thread(target=self.exe_send())
        # t2.start()
        self.core.mining()

    def exe_send(self):
        self.wallet.send(self.address, '14LSK4hmJghm5RqXjBFfGuJgAjZGNaKC3r', 10)

    def balance(self):
        balance = self.wallet.search_balance(self.address)
        print('잔액 : ', balance)

app = App()
app.start()
app.exe_send()
app.start()
app.balance()
# app.exe_send()
# app.start()
# app.exe_send()




# blockchain = BlockChain()
# t1 = threading.Thread(target=blockchain.mining())
# t1.start()

# #어떤 요청이 어떤 데이터와 들어왔을때, 어떤 페이지로 어떤데이터를 보내줄 것인지.
# #flask : webserver
# app = Flask(__name__)
# @app.route('/') #요청
# def index():
#     print('요청이 들어옵니까')
#     return render_template('index.html', result={'a':10, 'b':20}) #a=10, b=20 이라는 dictionary를 만들어서 보냄.
#
# @app.route('/hello')
# def hello():
#     b = Block()
#     b.gen_hash()
#     return jsonify(str(b))
#
# app.run(host='0.0.0.0', port=8080) #0.0.0.0(localhost) or 본인의 ip 입력

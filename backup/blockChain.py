# 채굴 클래스 : 채굴 프로그램 가동

# 제네시스 마이닝
#  - 채굴자의 지갑주소로 50btc 송금
#  - 제네시스 트랜잭션 : in값 = genesis, out값 : 채굴자 지갑주소, 50btc
#  - 제네시스 다음 트랜잭션 : in값 = utxo. (hash : 제네시스 transaction의 hash, n=2, address : 내주소, pubk : 내퍼블릭키, pubk_hs : 내 퍼블릭키 해시값)
#  - 트랜잭션 mempool에 추가
#  - 제네시스 블록 생성
#  - 트랜잭션 추가

from backup.block import Block
import threading
from backup import transaction as tr
from bitcoin import *

class Core(threading.Thread):
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.block = None

    def mining(self):
        nounce = 0
        bits = 3
        # while True :
        nounce += 1
        h = hashlib.sha256(str(nounce).encode()).hexdigest()
        print(nounce)
        # if h[:bits] == '0' * bits:
        # 만족하는 해시값 찾으면
        print('블록생성!')
        self.block = Block()
        self.block.nounce = nounce
        self.block.bits = bits
        self.block.hash = hashlib.sha256(str(self.block).encode()).hexdigest()
        # 블록값 세팅 (리워드 트랜잭션, 이전블록해시, 메모리풀 트랜잭션 이동, 머클루트)
        self.block_setting()
        if self.block.hash is not None:
            if self.block.prev_hash is None:    #genesis 블록 생성
                print('1. 제네시스 마이닝! ')
                print('   제네시스 블록 해시값 : ', self.block.hash)
            else:                               #블록 생성
                print('1. 블록 마이닝!')
                print('   블록 해시값 : ', self.block.hash)

        print('2. 블록정보:', self.block.__dict__)
        self.chain.append(self.block)
        print('block setting의 트랜잭션 수', len(self.block.transactions))
        # time.sleep(3)

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys = True) #문자열임. 정렬

    def block_setting(self):
        self.reward()
        if len(self.chain) > 0 :
            print('이전블록 해시값:', self.chain[len(self.chain) - 1].hash)
            self.block.prev_hash = self.chain[len(self.chain)-1].hash
        # self.block.mrkl_root = self.block.gen_mrkl_root()
        self.block.transactions = self.mempool
        print('block setting의 트랜잭션 수 값',len(self.block.transactions))
        self.mempool = []

    #reward transaction control
    def reward(self):
        print('########## 제네시스 트랜잭션 ###########')
        reward_out = tr.Transaction()
        out_data = tr.TxOut()
        out_data.value = 50
        out_data.to = '1NSCxgvbDBHwtbVsiMZT11N577tBxWNPRZ'
        reward_out.outputs.append(out_data)
        reward_out.vout_size = len(reward_out.outputs)
        reward_out.gen_hash()
        self.mempool.append(reward_out)
        print('-- out 항목 : ', reward_out.__dict__)

        reward_in = tr.Transaction()
        in_data = tr.TxIn()
        in_data.value = out_data.value
        in_data.address = out_data.to
        in_data.hash = reward_out.hash
        reward_in.inputs.append(in_data)
        reward_in.vin_size = len(reward_in.inputs)
        self.mempool.append(reward_in)
        print('-- in 항목 : ', reward_in.__dict__)


class Wallet:
    def __init__(self,core):
        self.core = core
        # self.block = core.block
        self.tr_input = tr.TxIn()
        self.tr_output = None
        # self.utxos = []
        # self.remain = 0


    #mempool에 트랜잭션 추가
    def add_transaction(self, tran):
        print('####### 트랜잭션 추가 ########')
        self.core.mempool.append(tran)

    #utxo찾기. 송금
    def utxo_control(self, my_address, privk):
        print('# --------1. 송금 utxo 찾기 시작~!---------- #')
        temps = []
        remain = 0
        tran = tr.Transaction()
        print(' # 2. core 객체 값 : ', self.core.__dict__)
        print(' #  2.1 chain 길이(블록 수) : ', len(self.core.chain))
        for block in self.core.chain:
            # out의 주소값이 내 주소값인 transaction 찾기
            print(' # 3. 체인에서 블록꺼내기', block.__dict__)
            print(' # 4. 블록내 트랜잭션 수: ', len(block.transactions))
            for transaction in block.transactions:
                print(' # 5. 트랜잭션 속성값들 : ', transaction.__dict__)
                for tr_out in transaction.outputs:
                    if tr_out.to == my_address:
                        print(' # 6. 나에게 보낸 트랜잭션 찾기')
                        temps.append(transaction.hash)
            # 위에서 찾은 트랜잭션의 hash를 트랜잭션 in의 hash에서 찾고 그 트랜잭션 중 out값이 비어있는 값 찾기 (UTXO 찾기)
            for transaction in block.transactions:
                print(' # 7. 다시 트랜잭션 탐색 : ', transaction.__dict__)
                if len(transaction.inputs) == 0:
                    continue
                print('transaction값 pass확인', transaction.__dict__)
                for input in transaction.inputs:
                    print(' # 8. 현트랜잭션 input값 : ', input.__dict__)
                    for temp in temps:
                        if input.hash == temp:
                            print(' # 9.이전트랜잭션hash == 현트랜잭션input.hash')
                            if len(transaction.outputs) == 0:   #utxo인 경우
                                for tr_input in transaction.inputs:  # in값들 찾아서 remain에 합산
                                    remain += tr_input.value
                                    print(' # 10. utxo 잔고 총합 :', remain)

                                #송금
                                ##트랜잭션 찾을때 마다 기존 트랜잭션의 out항목에 add
                                tr_output = tr.TxOut()  # txout객체 새로생성
                                tr_output.value = remain  # 잔액을 txout의 value에 복사
                                tr_output.to = my_address  # 보낼주소(내주소)도 복사
                                transaction.outputs.append(tr_output)  # transaction에 포함
                                transaction.vout_size = len(transaction.outputs)
                                transaction.gen_hash()
                                print(' # 11.1 기존 트랜잭션 속성값들(in o, out o) : ', transaction.__dict__)

                                #트랜잭션 찾을때 마다 새로운 트랜잭션의 in항목에 add
                                self.in_setting(transaction.hash, my_address, remain)       # 새로운 transaction 값 세팅
                                tran.gen_sign(privk)                                        # sign생성
                                tran.validate_chk()                                         # 유효성 체크
                                tran.inputs.append(self.tr_input)                           # 새 transaction의 in항목에 값 추가
                                tran.vin_size = len(transaction.inputs)
                                print(' # 11.2 새로운 트랜잭션 속성값들(in o, out x) : ', tran.__dict__)
                                self.add_transaction(tran)  #중간 다리 트랜잭션 멤풀에 추가
                                return tran

    def utxo_remain(self, my_address):
        print('# --------1. 잔액 utxo 찾기 시작~!---------- #')
        temps = []
        remain = 0
        tran = tr.Transaction()
        print(' # 2. core 객체 값 : ', self.core.__dict__)
        print(' #  2.1 chain 길이(블록 수) : ', len(self.core.chain))
        for block in self.core.chain:
            # out의 주소값이 내 주소값인 transaction 찾기
            print(' # 3. 체인에서 블록꺼내기', block.__dict__)
            print(' # 4. 블록내 트랜잭션 수: ', len(block.transactions))
            for transaction in block.transactions:
                print(' # 5. 트랜잭션 속성값들 : ', transaction.__dict__)
                for tr_out in transaction.outputs:
                    if tr_out.to == my_address:
                        print(' # 6. 나에게 보낸 트랜잭션 찾기')
                        temps.append(transaction.hash)
            # 위에서 찾은 트랜잭션의 hash를 트랜잭션 in의 hash에서 찾고 그 트랜잭션 중 out값이 비어있는 값 찾기 (UTXO 찾기)
            for transaction in block.transactions:
                print(' # 7. 다시 트랜잭션 탐색 : ', transaction.__dict__)
                if len(transaction.inputs) == 0:
                    continue
                    print('transaction값 pass확인', transaction.__dict__)
                for input in transaction.inputs:
                    print(' # 8. 현트랜잭션 input값 : ', input.__dict__)
                    for temp in temps:
                        if input.hash == temp:
                            print(' # 9.이전트랜잭션hash == 현트랜잭션input.hash')
                            if len(transaction.outputs) == 0:   #utxo인 경우
                                print(' # 10. utxo인것')
                                for tr_input in transaction.inputs:  # in값들 찾아서 remain에 합산
                                    remain += tr_input.value
                                    print('utxo 잔고 총합 :', remain)
                                    return transaction

    #트랜잭션 in 값 세팅
    def in_setting(self, hash, address, value):
        self.tr_input.hash = hash
        self.tr_input.address = address
        self.tr_input.n += 1
        self.tr_input.value = value

    def send(self, my_privk, my_addr, reciever_addr, coin):
        transaction = self.utxo_control(my_addr, my_privk)
        balance = 0
        for input in transaction.inputs:
            balance += input.value
        print('보내기 전 잔고:', balance)

        if coin > balance :
            raise Exception

        if coin == balance:
            tr_output = tr.TxOut()
            tr_output.value = coin
            tr_output.to = reciever_addr
            transaction.outputs.append(tr_output)
            transaction.gen_hash()
            self.in_setting(transaction.hash, reciever_addr, coin)
            self.add_transaction(transaction)

        else :
            #수신자
            tr_output = tr.TxOut()
            tr_output.value = coin
            tr_output.to = reciever_addr
            transaction.outputs.append(tr_output)
            self.in_setting(transaction.hash, reciever_addr, coin)
            self.add_transaction(transaction)

            #송신자 잔액
            tr_output1 = tr.TxOut()
            tr_output1.value = balance - coin
            tr_output1.to = my_addr
            transaction.outputs.append(tr_output1)
            transaction.vout_size = len(transaction.outputs)
            transaction.gen_hash()
            self.in_setting(transaction.hash, my_addr, coin)
            self.add_transaction(transaction)




    def search_balance(self, my_addr):
        transaction = self.utxo_remain(my_addr)
        balance = 0
        print('search_balance : ', transaction.__dict__)
        for input in transaction.inputs:
            balance += input.value

        print("잔액 : ", balance)


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
        self.wallet.send(self.privk, self.address, '14LSK4hmJghm5RqXjBFfGuJgAjZGNaKC3r', 10)

    def balance(self):
        self.wallet.search_balance(self.address)

app = App()
app.start()
app.exe_send()
app.start()
# app.balance()
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

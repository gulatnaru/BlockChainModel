import time
import hashlib
import json     #dictionary 를 json으로 만들 수 있도록 제공해주는 라이브러리
import threading

class Block():
    def __init__(self):
        self.prev_hash = None
        self.timestamp = time.time()
        self.mrkl_root = None
        self.bits = 2
        self.nounce = 0
        self.hash = None
        self.transactions = []

    # def add_transaction(self, transaction):
    #     self.transactions.append(transaction)

    def gen_mrkl_root(self):
        data_len = len(self.transactions)
        tmp_merkle = []
        for t in self.transactions:
            print(t.hash)
            tmp_merkle.append(t.hash)

        if data_len % 2 != 0:
            tmp_merkle.append(tmp_merkle[-1])

        while len(tmp_merkle) != 1:
            tmp = []
            for i in range(0, len(tmp_merkle), 2):
                tmp.append(hashlib.sha256((tmp_merkle[i] + tmp_merkle[i+1]).encode()).hexdigest())
                tmp_merkle = tmp
                print('머클트리 : '+tmp_merkle)

        self.mrkl_root = tmp_merkle[0]


    def gen_hash(self):
        while True :
            h = hashlib.sha256(str(self).encode()).hexdigest()
            self.nounce += 1
            print(self.nounce)
            if h[:self.bits] == '0' * self.bits:
                self.hash = h
                print('블록생성!')
                break

    #이 값을 현재 객체 상태에 대한 json으로 만들것.
    def __str__(self):
        return json.dumps(self.__dict__, sort_keys = True) #문자열임. 정렬

    # def test_gen_hash(self):
    #     self.hash = hashlib.sha256(str(self).encode()).hexdigest()

if __name__ == '__main__':
    b = Block()
    # tran = tr.Transaction()
    # b.add_transaction(tran)
    # b.add_transaction('World')
    # b.gen_hash()
    # b.gen_mrkl_root()
    t1 = threading.Thread(target=b.gen_hash())
    t1.start()
    # print(b)
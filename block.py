import time
import hashlib
import json     #dictionary 를 json으로 만들 수 있도록 제공해주는 라이브러리
import copy

class Block():
    def __init__(self):
        self.hash = None
        self.prev_hash = None
        self.merkle_root = None
        self.bits = 1
        self.nounce = 0
        self.timestamp = time.time()
        self.transactions = []

    def add_transaction(self, mempoolTrans):
        self.transactions = mempoolTrans

    def gen_mrkl_root(self):
        merkleTree = []
        tmp = []

        for t in self.transactions:
            merkleTree.append(t.hash)
            #test print
            print('----merkle tree print----')
            print(t.hash, ', ', end=' ')

        while len(merkleTree) != 1:
            # 트랜잭션의 개수가 홀수인 경우 마지막 트랜잭션의 tx_id를 하나 더 붙여줌.
            if len(merkleTree) % 2 == 1:
                merkleTree.append(merkleTree[len(merkleTree) - 1])
            for i in range(0, len(merkleTree), 2):
                tmp.append(hashlib.sha256((merkleTree[i] + merkleTree[i + 1]).encode()).hexdigest())
                print(tmp[i], ', ', end=' ')
            merkleTree = tmp
            tmp.clear()
        self.merkle_root = merkleTree[0]

    def gen_hash(self):
        while True :
            h = hashlib.sha256(str(self).encode()).hexdigest()
            self.nounce += 1
            print(self.nounce)
            if h[:self.bits] == '0' * self.bits:
                self.hash = h
                print('블록생성!')
                break

    def __str__(self):
        return json.dumps(self, default=self.dict_s, sort_keys = True)

    def dict_s(self, n):
        temp = copy.deepcopy(n.__dict__)
        if 'hash' in temp:
            del temp['hash']
        return temp

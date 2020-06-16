from MerkleTree import get_hash,create_merkle_tree,verify_transaction_given_merkle_tree_and_merkle_root
import random
def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))
class Block():
    
    def __init__(self,proof_of_work_zeros,index,narry,transactions,previous_block_hash):
        self.previous_block_hash = previous_block_hash
        self.narry = narry
        self.transactions = transactions
        self.merkle_tree = create_merkle_tree([item.txid for item in self.transactions],self.narry) #### given the list of transactions, create their hashes and get the
        self.merkle_tree_root = self.merkle_tree[-1][0]
        self.index = index
        self.pow_number_of_zeros = proof_of_work_zeros
        print("computing proof of work")
        self.compute_proof_of_work()
        self.transactions_count = len(self.transactions)
        self.block_reward = None
        self.fee_reward = None
    def compute_proof_of_work(self):
        self.block_hash = ''
        self.nounce = 0
        while count_leading_zero_string(self.block_hash) != self.pow_number_of_zeros:
            string = self.merkle_tree_root + self.previous_block_hash + str(self.nounce)
            self.block_hash = get_hash(string)
            self.nounce += 1
            if self.nounce%1000000 == 0:
                print("done nounce,", self.nounce)
        self.nounce = self.nounce - 1
        
        
class BlockChain():
    def __init__(self,narry,proof_of_work_zeros):
        self.proof_of_work_zeros = proof_of_work_zeros
        self.narry= narry
        self.blockchain = []
        self.blockchain.append(self.genesis_block())
    def genesis_block(self):
        return Block(self.proof_of_work_zeros,0,self.narry,['dummy'],'0')
        
    def add_block(block):
        #### code for verifing the new block
        #### Add the code in blockchain if verified #####
        self.blockchain.append(block)  #### also need to see if block is referencing to previous member of block, forking will happen
        
        
from MerkleTree import generate_hash,create_merkle_tree,verify_transaction_given_merkle_tree_and_merkle_root
import random


def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))
class Block():
    
    def __init__(self,proof_of_work_zeros,index,narry,transactions,previous_block_hash,hash_type,block_type="Regular"):
        self.block_type = block_type
        self.previous_block_hash = previous_block_hash
        self.narry = narry
        self.index = index
        self.pow_number_of_zeros = proof_of_work_zeros
        self.block_reward = None
        self.fee_reward = None
        self.hash_type = hash_type
        self.transactions = transactions
        self.transactions_count = len(self.transactions)
        self.merkle_tree = create_merkle_tree([item.txid for item in self.transactions],self.narry,hash_type) #### given the list of transactions, create their hashes and get the merkle tree
        self.merkle_tree_root = self.merkle_tree[-1][0]

        print("computing proof of work")
        self.compute_proof_of_work()
        print("computed")
    def __str__(self):
        rep = "Block: \n"
        for key, value in vars(self).items():
            if key not in ['merkle_tree']:
                rep += key + " --> "
                if type(value) is list:
                    rep += "list: "
                    for row in value:
                        rep += str(row)
                        rep += " , "
                else:
                    rep += str(value)
                rep += "\n"
        return rep
    def compute_proof_of_work(self):
        self.block_hash = ''
        self.nounce = 0
        while count_leading_zero_string(self.block_hash) != self.pow_number_of_zeros:
            string = self.merkle_tree_root + self.previous_block_hash + str(self.nounce)
            self.block_hash = generate_hash(string,type=self.hash_type)
            self.nounce += 1
            if self.nounce%1000000 == 0:
                print("done nounce,", self.nounce)
        self.nounce = self.nounce - 1
        
        
class BlockChain():
    def __init__(self,narry,proof_of_work_zeros,hash_type):
        self.proof_of_work_zeros = proof_of_work_zeros
        self.narry= narry
        self.hash_type = hash_type
        self.blockchain = []
        #print("Members of this block chain will need to compute {} proof of work zeros,".format(str(self.proof_of_work_zeros)))
        #self.blockchain.append(self.genesis_block())
        
    def __str__(self):
        rep = "BlockChain: [\n"
        for key, value in vars(self).items():
            rep += key + " --> "
            if type(value) is list:
                rep += "list: \n"
                for row in value:
                    rep += str(row)
                    rep += " , "
            else:
                rep += str(value)
            rep += "\n"
        rep += ']\n'
        return rep
    def add_genesis_block(self,t_genesis): 
        self.blockchain.append(Block(self.proof_of_work_zeros,0,self.narry,t_genesis,'0',self.hash_type,'Genesis'))
    def add_block(block):
        self.blockchain.append(block)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        #### added block must be verified at node level then it can be added to the blockchain
        #### Add the code in blockchain if verified #####
        
        ### if block is referencing to a last chain then it can be added otherwise , duplicate the whole chain till last reference and keep from there.  If there is consensus of long chains the remove all other forked chains!!!
         #### also need to see if block is referencing to previous member of block, forking will happen
        
        
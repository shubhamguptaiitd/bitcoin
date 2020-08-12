import time
from Message import Message
from Transaction import Transaction,Input,Output
from BlockChain import Block,BlockChain
from crypto_functions import generate_public_private_keys
from MerkleTree import generate_hash
import random
def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))


class Miner():
    def __init__(self,id,N,narry,prowk,hash_type,confirmation_blocks,private_key,public_keys_of_nodes,node_id_of_public_key,debug=False):
        self.id = id
        self.N = N
        self.narry = narry
        self.debug = debug
        self.proof_of_work_zeros = prowk
        self.hash_type = hash_type
        self.block_reward = 10
        self.confirmation_blocks = confirmation_blocks
        self.transaction_fee = 1
        self.block_creation_time = 10
        self.blockchain = None
        self.transactions_collected = []
        self.blocks_collected = []
        self.private_key= private_key
        self.public_keys_of_nodes = public_keys_of_nodes
        self.node_id_of_public_key = node_id_of_public_key
        self.forked_chain = [] #### this will be used to maintain forked version Assumption 
        print("Initialized miner for node,", self.id)
        
    def verify_genesis_block(self):
        return self.is_proof_of_work_correct(self.blockchain.blockchain[0]) and self.verify_transactions(self.blockchain.blockchain[0])
        
    def is_proof_of_work_correct(self,block):
        string = generate_hash(block.merkle_tree_root + block.previous_block_hash + str(block.nounce),type=self.hash_type)
        return count_leading_zero_string(string) == self.proof_of_work_zeros
    
    def verify_transaction(self,transaction):
        for row in transaction.tx_in:
            if row.prev_output_tid + "-"+str(row.prev_output_index) not in self.blockchain.utxo and transaction.t_type!='COINBASE':
                return False

        signaure_verified = transaction.verify_sign_transaction()
        return signaure_verified
    
    def verify_transactions(self,block):
        for transaction in block.transactions:
            #print(self.id, transaction.txid)
            if not self.verify_transaction(transaction):
                return False
        #print(self.id , " Returning true for transaction verification")
        return True


    def create_block(self):
        in_btc = 0
        out_btc = 0
        #block_creation_award = 1
        if self.debug:
            print(self.id, "creating block of length ", len(self.transactions_collected))
        if len(self.transactions_collected) >= 1:
            for transact in self.transactions_collected:
                for ins in transact.tx_in:
                    amount = self.blockchain.get_amount_for_txid_and_index(ins.prev_output_tid,ins.prev_output_index)
                    if amount is None:
                        return None ### means referenced input transactions dont exist in verified blockchain
                    in_btc += amount
                for outs in transact.tx_out:
                    out_btc += outs.amount
            total_reward =self.block_creation_time + in_btc - out_btc
            inputs = [Input('None','None')]
            outputs = [Output(self.public_keys_of_nodes[self.id].hex(),total_reward,self.hash_type)]
            transaction = Transaction(self.public_keys_of_nodes[self.id],inputs,outputs,self.private_key,t_type = 'COINBASE',hash_type=self.hash_type)
            block = Block(self.proof_of_work_zeros,len(self.blockchain.blockchain),self.narry,[transaction] + self.transactions_collected ,self.blockchain.blockchain[-1].block_hash,self.hash_type,block_type="Regular")
            return block
        else:
            return None ### No transactions pending to be verified
        
    def verify_block(block):
        return self.is_proof_of_work_correct(block) and self.verify_transactions(block)

    def add_block(self,block):
        if self.is_proof_of_work_correct(block):
            if self.verify_transactions(block):
#                print(self.id, block.previous_block_hash, self.blockchain.blockchain[-1].block_hash)
                if block.previous_block_hash == self.blockchain.blockchain[-1].block_hash:
                    self.blockchain.blockchain.append(block)
                    self.blockchain.current_block_height += 1
                    if self.debug:
                        print(self.id," transaction already ,", len(self.transactions_collected))
                    #print(self.id," already ", [t.txid for t in self.transactions_collected])
                    for trans in block.transactions:
                        index = [index  for index,transaction in enumerate(self.transactions_collected) if transaction.txid == trans.txid]
                        #print(self.id, index)
                        if len(index) >=1 :
                            self.transactions_collected.pop(index[0])
                        if len(index) > 1:
                            print(self.id, " More than 1 index found , please check ")
                    #print(self.id , " left ", [t.txid for t in self.transactions_collected])
                    if self.debug:
                        print(self.id," transaction left now ,", len(self.transactions_collected))
                    return True
        return False
    def increase_verified_block(self):
        if self.blockchain.current_block_height > self.blockchain.confirmed_block_index:
            self.blockchain.confirmed_block_index += 1
            self.blockchain.add_utxos(self.blockchain.blockchain[self.blockchain.confirmed_block_index].transactions)
            self.blockchain.spent_utxos(self.blockchain.blockchain[self.blockchain.confirmed_block_index].transactions)
            return True
        else:
            return False

    
from multiprocessing import Process, Queue,Pool
import threading
import queue as Q
import time
import sys
from Message import Message
from Transaction import Transaction,Input,Output
from BlockChain import Block,BlockChain
from crypto_functions import generate_public_private_keys
from MerkleTree import generate_hash
import random
def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))
class Node():   ### This node can function as both worker and mining node!!!
    def __init__(self,id,N,narry,prowk,hash_type,debug=False):
        self.id = id
        self.N = N
        self.debug = debug
        self.narry = narry
        self.proof_of_work_zeros = prowk
        self.hash_type = hash_type
        ### Create a private and public key
        self.public_key,self.private_key = generate_public_private_keys()
        self.btc = 0 #### bitcoins it has
        self.blockChain = None
        self.transactions_collected = []   #### unspent transactions (it stores the ids of unspent transactions)
        
        

        
    def main(self,msg_qs,outputq):
        done = False
        self.public_keys_of_nodes = [None]*self.N
        self.public_keys_of_nodes[self.id]  = self.public_key
        self.received_transactions = []
        self.received_blocks = []
        
        #send each other the public  keys
        ct = 0
        for i in range(0,self.N):
            if i != self.id:
                msg_qs[i].put(Message("PUBLIC_KEY",self.public_key,self.id,i))
        ct =0
        while ct<self.N-1:
            try:
                msg = msg_qs[self.id].get(block=True,timeout=10)   
                if msg.type == "PUBLIC_KEY":
                    self.update_public_key_of_node(msg.src,msg.msg)
                    ct += 1
                
            except Q.Empty:
                print(" No message and wait for the public keys")
        if self.debug:
            print("Received public key with ct {} from every node to {}".format(str(ct),str(self.id)))
        
            
        
        if self.id == 0: ## create a genesis block
            inputs = [Input('None','None')]
            outputs = []
            total_amount_generated = 0
            for i in range(0,self.N):
                amount = random.choice(range(5,15))
                total_amount_generated += amount
                outputs.append(Output(self.public_keys_of_nodes[i].hex(),amount,self.hash_type))
            coinbase_t = Transaction(self.public_keys_of_nodes[self.id],inputs,outputs,self.private_key,t_type = 'COINBASE',hash_type=self.hash_type)
            self.blockchain = BlockChain(self.narry,self.proof_of_work_zeros,hash_type)
            self.blockchain.add_genesis_block([coinbase_t])
            for i in range(1,self.N) : ## Send everyone genesis block chain
                if self.debug:
                    print("Sending everyone else the genesis block ", self.id)
                msg_qs[i].put(Message("GENESIS_BLOCK",self.blockchain,self.id,i))
        else:  ### everyone else will receive the genesis block and use it further for transaction
            received_genesis_block = False
            while not received_genesis_block:
                try:
                    msg = msg_qs[self.id].get(block=True,timeout=10)   
                    if msg.type == "GENESIS_BLOCK":
                        self.blockchain = msg.msg
                        received_genesis_block = True

                except Q.Empty:
                    print(" Waiting for genesis block," , self.id)
                    
            if self.debug:
                print("Received genesis block, now need to verify it ", self.id)
                    
                    
                msg.msg.blockchain[0].nounce = '223'
                if self.verify_genesis_block(msg.msg):
                    
                    print("verfied genesis block")
                    self.blockchain = msg.msg
                
                
            
            
        #print("Done and return," , self.id)
        
                
            
            
            
            
            
            
            
            
            
            
            
            
            
        ### Genesis block will contain the transfer of bitcoins to all the nodes, all the nodes will receive the genesis block and append it to their blockchain
        
        ### Now node 0 will create a genesis block , this block will transfer the bitcoins to all the nodes, a random number between 0.1 BTC to 100000 BTC
        ### Now each node will select a random node and will send it money 
        ### Once it does send/receive then it wont send any money to any other node for 10 seconds
        ### Further each node will engange in mining the blocks, as soon it finishes, it will send the blocks to everyone and everyone will validate the block before adding it.
        ### Once they validate, 
#         while not done:
#             try:
#                 msg = msg_qs[self.id].get(block=True,timeout=10)
#                 if msg.type == "PUBLIC_KEY":
#                     self.update_public_key_of_node(msg.src,msg.msg)
#                 if msg.type == "TRANSACTION":
#                     #### collect the transaction ###
#                 if msg.type == "BLOCK":
#                     ### add the block and verify it
                    
                
#                 #print("Received message")
#                 print("Received message  ," +str(msg))
#                 ct += 1
#             except Q.Empty:
#                 print("No new message in 5 seconds , got messages from {} exitin {}".format(str(ct),str(self.id)))
#                 #outputq.put("I am done {}".format(str(self.id)))
#                 done = True
#                 #return
        
    def verify_genesis_block(self,blockchain):
        return self.is_proof_of_work_correct(blockchain.blockchain[0]) and self.verify_transactions(blockchain.blockchain[0])
    def is_proof_of_work_correct(self,block):
        string = generate_hash(block.merkle_tree_root + block.previous_block_hash + str(block.nounce),type=self.hash_type)
        return count_leading_zero_string(string) == self.proof_of_work_zeros
    
    def verify_transaction(self,transaction):
        if transaction.t_type=='COINBASE':
        for row in transaction.tx_in:
            if row.prev_output_tid not in self.blockChain.utxo:
                return False
        return transaction.verify_sign_transaction()
    
    def verify_transactions(self,block):
        for transaction in block.transactions:
            if not verify_transaction(transaction):
                return False
        return True
    
    def add_block(self,block):
        if proof_of_work_correct(block):
            if transactions_verified(block):
                print("added to block chain")
    
    def update_public_key_of_node(self,nodeid,public_key):
        self.public_keys_of_nodes[nodeid] = public_key
    ### code to add to block chain

if __name__== "__main__":
    debug = True
    number_of_nodes= int(sys.argv[1])
    narry = int(sys.argv[2])
    prowk = int(sys.argv[3])
    hash_type= sys.argv[4]
    qs = []
    if debug:
        print("Opening queues, " , number_of_nodes)
    for i in range(0, number_of_nodes):
        qs.append(Queue())

    outputq = Queue()
    nodes= [Node(id,number_of_nodes,narry,prowk,hash_type,debug) for id in range(0,number_of_nodes)]
    processes = [Process(target=nodes[id].main, args=(qs,outputq,)) for id in range(number_of_nodes)]
    # Run processes
    for p in processes:
        p.start()
    if debug:
        print("started all process")

    for p in processes:
        p.join()       # Exit the completed processes
    if debug:
        print("Joined all process")
#     for p in processes:
#         p.close()
    #outputs = [outputq.get() for p in processes]
    #print(outputs)
    
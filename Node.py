
import time
from Message import Message
from Transaction import Transaction,Input,Output
from BlockChain import Block,BlockChain
from crypto_functions import generate_public_private_keys
from MerkleTree import generate_hash
import random
def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))
def coin_toss(prob):
    if random.uniform(0,1) <= prob:
        return True
    else:
        return False
def pick_receiver(id,N):
    receiver= id
    while receiver != id:
        receiver = random.randint(0,N-1)
    return receiver



class Node():   ### This node can function as both worker and mining node!!!
    def __init__(self,id,N,narry,prowk,hash_type,confirmation_blocks,debug=False):
        self.id = id
        self.N = N
        self.debug = debug
        self.narry = narry
        self.proof_of_work_zeros = prowk
        self.hash_type = hash_type
        self.block_reward = 10
        self.confirmation_blocks = confirmation_blocks
        self.transaction_fee = 1
        self.block_creation_time = 10
        self.public_key,self.private_key = generate_public_private_keys()
        self.public_key_hash = generate_hash(self.public_key.hex(),type = hash_type)
        self.btc = 0 
        self.unspent_btc = {}
        
    def update_public_key_of_node(self,nodeid,public_key):
        self.public_keys_of_nodes[nodeid] = public_key
        self.node_id_of_public_key[public_key] = nodeid
        
    def main(self,msg_qs,outputq):
        done = False
        self.public_keys_of_nodes = [None]*self.N
        self.public_keys_of_nodes[self.id]  = self.public_key
        self.node_id_of_public_key = {}
        self.node_id_of_public_key[self.public_key] = self.id
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
            print("Received public key total from ct {} from every node to {}".format(str(ct),str(self.id)))
            
        miner = Miner(self.id,self.N,self.narry,self.proof_of_work_zeros,self.hash_type,self.public_keys_of_nodes,self.node_id_of_public_key,self.debug=False)
        if self.id == 0: ## create a genesis block
            inputs = [Input('None','None')]
            outputs = []
            total_amount_generated = 0
            for i in range(0,self.N):
                
                amount = random.choice(range(20,60))
                if i ==0:
                    amount += self.block_reward
                total_amount_generated += amount
                outputs.append(Output(self.public_keys_of_nodes[i].hex(),amount,self.hash_type))
            coinbase_t = Transaction(self.public_keys_of_nodes[self.id],inputs,outputs,self.private_key,t_type = 'COINBASE',hash_type=self.hash_type)
            self.blockchain = BlockChain(self.narry,self.proof_of_work_zeros,hash_type)
            self.blockchain.add_genesis_block([coinbase_t])
            for i in range(1,self.N) : ## Send everyone genesis block chain
                if self.debug:
                    print("Sending everyone else the genesis block ", self.id)
                msg_qs[i].put(Message("GENESIS_BLOCK",self.blockchain,self.id,i))
            self.update_unspent_btc_from_blockchain(self.blockchain)
        else:                                          ### everyone else will receive the genesis block and use it further for transaction
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
                print("Received genesis block, now need to verify it and update its own money ", self.id)
                #msg.msg.blockchain[0].nounce = '223'
            if self.verify_genesis_block(msg.msg):
                    
                print("verfied genesis block")
                ### identify people from whom you got money
                #self.blockchain = msg.msg
                self.update_unspent_btc_from_blockchain(self.blockchain)
                
                

        done = False
        die_out_seconds = 30
        timeout_seconds = 1
        last_block_cor = time.time() ### time of last time block was created or received
        last_transaction_time = time.time()
        waited_time = 0
        while not done:
            try:    
                msg= msg_qs[self.id].get(block=True,timeout=timeout_seconds)   
                waited_time = 0
                if msg.type == "Transaction":
                    if msg.msg.verify_sign_transaction():
                        self.transactions_collected.append(msg.msg)
                    # if msg.type == "Block":
                    #     last_block_cor = time.time()
                    #     new_block = msg.msg
                    #     self.verify_block(new_block)
                   # store_it_
            except Q.Empty:
                waited_time += timeout_seconds
                
                if waited_time > die_out_seconds:
                    print("waited for transactions for more than ",die_out_seconds,"  seconds, seems none is using bitcoin, lets die")
                    print("I {} had a amount of {} BTC".format(str(self.id),str(self.btc)))
                    return
                else:  ## stuff to do , may be create a block or receive a block , send some poor chap a money   
                    if coin_toss(1.0/self.N):
                        
                    
                    if time.time() - last_block_cor > self.block_creation_time:
                        last_block_cor= time.time()
                        if coin_toss(5*1.0/self.N):
                            print("creating a block and send it everyone,", self.id)
                            # new_block = self.create_block()
                            
                            # self.transactions_collected = []
                            #print("Before sending it to everyone do check if someone has sent you already")
                            
                            

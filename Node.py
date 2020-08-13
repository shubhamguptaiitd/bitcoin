import queue as Q
import time
from Message import Message
from Transaction import Transaction,Input,Output
from BlockChain import Block,BlockChain
from crypto_functions import generate_public_private_keys
from MerkleTree import generate_hash
from Miner import Miner
import random
def coin_toss(prob):
    if random.uniform(0,1) <= prob:
        return True
    else:
        return False
def pick_receiver(id,N):
    receiver= id
    while receiver == id:
        receiver = random.randint(0,N-1)
    return receiver



class Node():   ### This node can function as both worker and mining node!!!
    def __init__(self,id,N,narry,prowk,hash_type,confirmation_blocks,num_msg_limit,msg_ct_list,debug=False):
        self.id = id
        self.N = N
        self.debug = debug
        self.narry = narry
        self.proof_of_work_zeros = prowk
        self.hash_type = hash_type
        self.block_reward = 10
        self.confirmation_blocks = confirmation_blocks
        self.transaction_fee = 1
        self.block_creation_time = 30
        self.public_key,self.private_key = generate_public_private_keys()
        self.public_key_hash = generate_hash(self.public_key.hex(),type = hash_type)
        self.btc = 0 
        self.unspent_btc = {}
        self.msg_ct_limit = num_msg_limit
        self.msg_ct_list = msg_ct_list
        self.start_time = time.time()
    def time_spent(self):
        return int(time.time() - self.start_time)
    def update_public_key_of_node(self,nodeid,public_key):
        self.public_keys_of_nodes[nodeid] = public_key
        self.node_id_of_public_key[public_key] = nodeid
    def update_unspent_btc_from_block(self,block): ### only called when block is confirmed
        for tx in block.transactions:
            txid = tx.txid
            sender_address = bytes.fromhex(tx.sender_address)
            for index,output in enumerate(tx.tx_out):
                if output.to_address == self.public_key_hash:
                    key = txid+"-"+str(index)
                    if key not in self.unspent_btc:
                        if tx.t_type == "COINBASE":
                            print("{} Received {} BTC as block creation reward".format(str(self.id),str(output.amount)))
                        else:
                            if self.id != self.node_id_of_public_key[sender_address]:
                                print("{} Received {} BTC from {}".format(str(self.id),str(output.amount),self.node_id_of_public_key[sender_address]))
                        self.unspent_btc[key] = [sender_address,output.amount,txid,index]
                        self.btc += output.amount
                    else:
                        print("RED ALERT:already received money from this transaction,",  self.id)
                        
            if sender_address == self.public_key and tx.t_type !='COINBASE':
                for index,input in enumerate(tx.tx_in):
                    key = input.prev_output_tid +"-"+str(input.prev_output_index)
                    self.btc -= self.unspent_btc[key][1]
                    if self.last_transaction_key is not None:
                        if key == self.last_transaction_key:
                            self.last_transaction_verified = True
                            print("{} verified last transaction".format(str(self.id)))
                            self.last_transaction_key = None
                    #print("{} have received  {} awards BTC".format(str(self.id),str(self.btc)))
                    del self.unspent_btc[key]
                    
    def print_self_balance(self):
        total_balance = 0
        for key in self.unspent_btc.keys():
            total_balance += self.unspent_btc[key][1]
        print("{} has balance of {} BTC".format(str(self.id),str(total_balance)))
    def main(self,msg_qs,outputq):
        
#         print(self.id, len(self.msg_ct_list))
#         self.msg_ct_list.append(self.id)
#         print(self.id, self.msg_ct_list)
        done = False
        self.public_keys_of_nodes = [None]*self.N
        self.public_keys_of_nodes[self.id]  = self.public_key
        self.node_id_of_public_key = {}
        self.node_id_of_public_key[self.public_key] = self.id
        self.last_transaction_verified = True
        self.last_transaction_key = None
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
            
        miner = Miner(self.id,self.N,self.narry,self.proof_of_work_zeros,self.hash_type,self.confirmation_blocks,self.private_key,self.public_keys_of_nodes,self.node_id_of_public_key,self.debug)
        debug_block_creation_time = True
        if self.id == 0: ## create a genesis block
            inputs = [Input('None','None')]
            outputs = []
            total_amount_generated = 0
            print("Initial money")
            for i in range(0,self.N):
                amount = 1000
                if i == 0:
                    amount += self.block_reward
                total_amount_generated += amount
                print(i, amount)
                outputs.append(Output(self.public_keys_of_nodes[i].hex(),amount,self.hash_type))
            coinbase_t = Transaction(self.public_keys_of_nodes[self.id],inputs,outputs,self.private_key,t_type = 'COINBASE',hash_type=self.hash_type)
            miner.blockchain = BlockChain(self.narry,self.proof_of_work_zeros,self.hash_type)
            if debug_block_creation_time:
                start_time_block = time.time()
            miner.blockchain.add_genesis_block([coinbase_t])
            if debug_block_creation_time:
                print("Time taken in genesis block creation,", time.time()-start_time_block)
            for i in range(1,self.N):
                if self.debug:
                    print("Sending everyone else the genesis block ", self.id)
                msg_qs[i].put(Message("GENESIS_BLOCK",miner.blockchain,self.id,i))
            self.update_unspent_btc_from_block(miner.blockchain.blockchain[0])
        else:                                                                                         ### everyone else will receive the genesis block and use it further for transaction
            received_genesis_block = False
            while not received_genesis_block:
                try:
                    msg = msg_qs[self.id].get(block=True,timeout=10)   
                    if msg.type == "GENESIS_BLOCK":
                        miner.blockchain = msg.msg
                        received_genesis_block = True

                except Q.Empty:
                    print(" Waiting for genesis block," , self.id)    
            if self.debug:
                print("Received genesis block, now need to verify it and update its own money ", self.id)
                #msg.msg.blockchain[0].nounce = '223'
            if miner.verify_genesis_block():
                if self.debug:
                    print("verfied genesis block")
                self.update_unspent_btc_from_block(miner.blockchain.blockchain[0])
                

        done = False
        die_out_seconds = 120
        timeout_seconds = 1
        start_time = time.time()
        last_block_cor = time.time() 
        last_transaction_time = time.time()
        waited_time = 0
        debug_size = False
        debug_multi_transaction = False
        if debug_size and self.id == 0:
                print(self.id, " size of block chain ", miner.blockchain.size())
        while not done:
            try:    
                #print(self.id , "main checking for message")
                msg= msg_qs[self.id].get(block=True,timeout=timeout_seconds)   
                waited_time = 0
                if msg.type == "Transaction":
                    #print(self.id,"Transaction has been received from ", msg.src )
                    if msg.msg.verify_sign_transaction():
                        miner.transactions_collected.append(msg.msg) ###check if already exist in blockchain
                        last_transaction_time = time.time()
                elif msg.type == "Block":
                    print(self.id , "Block has been received from", msg.src)
                    status = miner.add_block(msg.msg)
                    if status:
                        print(self.id, " Received block has been added to blockchain ")
                        last_block_cor = time.time()
                    else:
                        print(self.id, " Received block was not added")
                else:
                    print(self.id, " Received message of type , I dont do what do i do with it", msg.type , msg.src)
                    
                        
            except Q.Empty:
                waited_time += timeout_seconds
                
                if waited_time > die_out_seconds:
                    print("waited for transactions for more than ",die_out_seconds,"  seconds, seems none is using bitcoin, lets die")
                    #print("I {} had a amount of {} BTC".format(str(self.id),str(self.btc)))
                    self.print_self_balance()
                    return
                else:  
                    if time.time() - last_transaction_time > 20 and self.last_transaction_verified :
                        if coin_toss(1.0/self.N):
                            self.msg_ct_list.append(self.id)
                            if len(self.msg_ct_list) <= self.msg_ct_limit:
                                send_to = pick_receiver(self.id,self.N)
                                amount = random.randint(1,4)
                                unspent_key = None
                                for key in self.unspent_btc.keys():
                                    if amount +3 <= self.unspent_btc[key][1]:
                                        unspent_key = key
                                if unspent_key is None:
                                    print("{} has no money left , so dying".format(str(self.id)))
                                else:
                                    #key = list(self.unspent_btc.keys())[0]
                                #print("{} has amount {} btc in selected key".format(str(self.id),str(self.unspent_btc[unspent_key][1])))
                                    if debug_multi_transaction:
                                        send_to_v = pick_receiver(self.id,self.N)
                                        inputs = [Input(self.unspent_btc[unspent_key][2],self.unspent_btc[unspent_key][3])]
                                        outputs = [Output(self.public_keys_of_nodes[send_to].hex(),amount,self.hash_type),Output(self.public_keys_of_nodes[send_to_v].hex(),amount+2,self.hash_type),Output(self.public_keys_of_nodes[self.id].hex(),self.unspent_btc[unspent_key][1]-amount-amount-2-1,self.hash_type)]
                                        print("Node {} Sending {} btc to node {} and {} btc to node {} ".format(str(self.id),str(amount),str(send_to),str(amount+2),str(send_to_v)))
                                    else:
                                        inputs = [Input(self.unspent_btc[unspent_key][2],self.unspent_btc[unspent_key][3])]
                                        outputs = [Output(self.public_keys_of_nodes[send_to].hex(),amount,self.hash_type),Output(self.public_keys_of_nodes[self.id].hex(),self.unspent_btc[unspent_key][1]-amount-1,self.hash_type)]
                                    
                                    transaction = Transaction(self.public_keys_of_nodes[self.id],inputs,outputs,self.private_key,t_type = 'Regular',hash_type=self.hash_type)
                                    for i in range(0, self.N):
                                        if i != self.id:
                                            msg_qs[i].put(Message("Transaction",transaction,self.id,i))
                                    miner.transactions_collected.append(transaction)
                                    self.last_transaction_verified = False
                                    self.last_transaction_key = unspent_key
                                    #del self.unspent_btc[key] #### check for this and
                                    last_transaction_time = time.time()
                                    print("Node {} Sending {} btc to node {} ".format(str(self.id),str(amount),str(send_to)))
                                    waited_time = 0

                    if time.time() - last_block_cor > self.block_creation_time:
                        #last_block_cor= time.time()
                        if coin_toss(1*1.0/self.N):
                            print(self.id, " Creating a block ", len(miner.transactions_collected))
                            new_block = miner.create_block()
                            if new_block is not None:
                                #
                                if self.debug:
                                    print(self.id, " block has been created but first check if someone computed first")
                                send_block_to_ee = False
                                empty_queue = False
                                temp_msgs = []
                                while not empty_queue:
                                    try:
                                        msg= msg_qs[self.id].get(block=True,timeout=timeout_seconds)
                                        if msg.type == "Block":
                                            if self.debug:
                                                print(self.id , " Ohh Received a block from ", msg.src)
                                            
                                            miner.add_block(msg.msg)
                                            empty_queue = True
                                        else:
                                            temp_msgs.append(msg)
                                    except Q.Empty:
                                        send_block_to_ee = True
                                        empty_queue = True
                                        for msg in temp_msgs:
                                            msg_qs[self.id].put(Message(msg.type,msg.msg,msg.src,msg.dst)) ## putting it back so can be fetched again in main loop

                                if send_block_to_ee:
                                    #if self.debug:
                                    waited_time = 0
                                    print(self.id, " No block has been recieved, so send it everyone")
                                    for i in range(0,self.N):
                                        if i != self.id:
                                            print(self.id, " sending created block to ", i)
                                            msg_qs[i].put(Message("Block",new_block,self.id,i))
                                    miner.add_block(new_block)
                                #last_block_cor = time.time()   
                        

                        res = miner.increase_verified_block()
                        #print(self.id, "after adding status",res)
                        last_block_cor = time.time()
                        if res:
                            if debug_size and self.id == 0:
                                print(self.id, " size of block chain after adding ", miner.blockchain.size())
                            self.update_unspent_btc_from_block(miner.blockchain.blockchain[miner.blockchain.confirmed_block_index]) ## it will 
                            ## also need to check if last payment by this node is verified
                            self.print_self_balance()
from multiprocessing import Process, Queue,Pool
import threading
import queue as Q
import time
import sys
from Message import Message
from Transactions import Transaction,Input,Output
from BlockChain import Block
from crypto_functions import generate_public_private_keys
from MerkleTree import generate_hash
def count_leading_zero_string(string):
    return len(string) - len(string.lstrip('0'))
class Node():   ### This node can function as both worker and mining node!!!
    def __init__(self,id,N,debug=False):
        self.id = id
        self.N = N
        ### Create a private and public key
        self.private_key,self.public_key = generate_public_private_keys()
        self.btc = 0 #### bitcoins it has
        self.blockChain = None
        self.transactions_collected = []   #### unspent transactions (it stores the ids of unspent transactions)
        self.proof_of_work_zeros = 6
        
    def is_proof_of_work_correct(self,block):
        string = generate_hash(block.merkle_tree_root + block.previous_block_hash + block.nounce)
        return count_leading_zero_string(string) == self.proof_of_work_zeros
    
    def verify_transaction(transaction):
        for row in transaction.tx_in:
            if row.prev_output_tid not in self.blockChain.utxo:
                return False
        return transaction.verify_sign_transaction()
    
    def verify_transactions(self,block):
        for transaction in block.transactions:
            if not verify_transaction(transaction):
                return False
        return True
    
    def add_block(self,Block block):
        if proof_of_work_correct(block):
            if transactions_verified(block):
                ### code to add to block chain
        
    def main(self,msg_qs,outputq):
        done = False

        print("{} is Putting a message to a neighbour".format(str(self.id)))
        msg_qs[(self.id+1)%self.N].put(Message("Add this to the transaction",self.id,(self.id+1)%self.N))
        while not done:
            try:
                msg = msg_qs[self.id].get(block=True,timeout=5)
                print("Received message  ," +str(msg))
            except:
                print("No new message in 5 seconds exitin {}".format(str(self.id)))
                outputq.put("I am done {}".format(str(self.id)))
                done = True
                return
        


# In[5]:

if __name__== "__main__":
    debug = False
    number_of_nodes= 10
    qs = []
    if debug:
        print("Opening queues, " , number_of_nodes)
    for i in range(0, number_of_nodes):
        qs.append(Queue())

    outputq = Queue()
    nodes= [BitNode(id,number_of_nodes,debug) for id in range(0,number_of_nodes)]
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
    outputs = [outputq.get() for p in processes]
    print(outputs)
    
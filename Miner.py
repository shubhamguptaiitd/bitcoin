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
    def __init__(self,id,N,narry,prowk,hash_type,debug=False):
        self.id = id
        self.N = N
        self.narray = narray
        self.proof_of_work_zeros = prowk
        self.hash_type = hash_type
        self.block_reward = 10
        self.confirmation_blocks = 3
        self.transaction_fee = 1
        self.block_creation_time = 10
        self.blockchain = None
        self.transactions_collected = []
        self.blocks_collected = []
        
        
        
        ### Create a private and public key
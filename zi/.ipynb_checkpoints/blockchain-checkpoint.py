class Block():
    def __init__(self,transactions):
        self.transactions = transactions
        self.merkle_tree = [] #### given the list of transactions, create their hashes and get the
        
        
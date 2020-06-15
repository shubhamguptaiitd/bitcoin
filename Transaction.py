##### It needs to be defined carefully

class Input():
    def __init__(self,)

class transaction:
    
    def __init__(self,gen):         #creates genesis transaction
        self.prev_hasht="genesist"
        self.trans_details=10
        self.rx_pub_key="abc"
        obj=self.prev_hasht+str(self.trans_details)+self.rx_pub_key
        self.hasht=hash(obj)
        #print(self.hasht)
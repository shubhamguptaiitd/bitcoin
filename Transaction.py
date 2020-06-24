from crypto_functions import generate_hash,generate_public_private_keys,key_in_RSA_object,sign_data,verify_sign


class Transaction():
    def __init__(self,sender_address,inputs,outputs,private_key):
        self.tx_in_ct = len(inputs)
        self.tx_in = inputs
        self.tx_out_ct = len(outputs)
        self.tx_out = outputs
        self.time = str(int(time.time()))
        self.sender_address = sender_address.hex()  ### sender_address/publickey in bytes
        self.sign = self.sign_transaction(key_in_RSA_object(private_key)) ### private_key is byte
        self.idx = generate_hash(str(self))
    def __str__(self):
        rep = self.time + str(self.tx_in_ct) + str(self.tx_out_ct) +"--"
        for tx in self.tx_in:
            rep+= str(tx)
        for tx in self.tx_out:
            rep+= str(tx)
        rep += self.sender_address
        return rep
    def sign_transaction(self,private_key):
        return sign_data(str(self),private_key)
    def verify_sign_transaction(self):
        return verify_sign(str(self),self.sign,key_in_RSA_object(bytes.fromhex(self.sender_address)))
        
        
class Input():
    def __init__(self,prev_output_tid,index):
        self.prev_output_tid = prev_output_tid
        self.prev_output_index = index
    def __str__(self):
        return str(self.prev_output_tid) + "--" + str(self.prev_output_index)
class Output():
    def __init__(self,to_address,amount): ###to_address is hexadecimal
        self.to_address = generate_hash(to_address)
        self.amount = amount
    def __str__(self):
        return str(self.to_address) +"--" +str(self.amount)

    


    

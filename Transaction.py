from crypto_functions import generate_hash,generate_public_private_keys,key_in_RSA_object,sign_data,verify_sign
import time

class Transaction():
    def __init__(self,sender_address,inputs,outputs,private_key,t_type,hash_type):   #### Since private key is not stored in class object, anyone who has this object will not be able to sign again the transaction since it wont have the private key
        self.t_type = t_type
        self.tx_in_ct = len(inputs)
        self.tx_in = inputs
        self.tx_out_ct = len(outputs)
        self.tx_out = outputs
        self.sender_address = sender_address.hex()  ### sender_address/publickey in bytes
        self.time = str(int(time.time()))
        self.hash_type = hash_type
        self.sign = self.sign_transaction(key_in_RSA_object(private_key)) ### private_key is byte
        self.txid = generate_hash(self.string_of_transaction(),type=hash_type)
    def string_of_transaction(self):
        rep = self.time + str(self.tx_in_ct) + str(self.tx_out_ct) +"--"
        for tx in self.tx_in:
            rep+= str(tx)
        for tx in self.tx_out:
            rep+= str(tx)
        rep += self.sender_address
        return rep
    def __str__(self):
        rep = "Transaction:[ \n"
        for key, value in vars(self).items():
            rep += key + " --> "
            if type(value) is list:
                rep += 'list: \n'
                for item in value:
                    rep += str(item)
                    rep += " , "
            else:
                rep += str(value)
            rep += "\n"
        rep += "]\n"
        return rep

    def sign_transaction(self,private_key):
        return sign_data(self.string_of_transaction(),private_key)
    def verify_sign_transaction(self):  ### since sign is made using private key, if it changes the data
        return verify_sign(self.string_of_transaction(),self.sign,key_in_RSA_object(bytes.fromhex(self.sender_address)))
        
        
class Input():
    def __init__(self,prev_output_tid,index):
        self.prev_output_tid = prev_output_tid
        self.prev_output_index = index
    def __str__(self):
        return "Input: prev_output_reference--> "+ str(self.prev_output_tid) + " -- index --> " + str(self.prev_output_index)
class Output():
    def __init__(self,to_address,amount,hash_type): ###to_address is hexadecimal
        self.to_address = generate_hash(to_address,type = hash_type)
        self.amount = amount
    def __str__(self):
        return "Output: receiver_address_hash--> " + str(self.to_address) +"-- amount in btc --> " +str(self.amount)

    


    

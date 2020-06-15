
from multiprocessing import Process, Queue,Pool
import threading
import queue as Q
import time
import sys


class Message():
    def __init__(self,type,src,dst): 
        self.type = type  ##### Add to block, 
        self.src = src 
        self.dst = dst

    def __str__(self):
        return self.type + ":" + str(self.src) + "->" + str(self.dst) 




class BitNode():
    def __init__(self,id,N,debug=False):
        self.id = id
        self.N = N
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
    
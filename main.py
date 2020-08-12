from Node import Node
from multiprocessing import Manager,Process, Queue,Pool
import threading
import queue as Q
import sys
debug = False
manager = Manager()
msg_ct_list = manager.list()
number_of_nodes= int(sys.argv[1])
narry = int(sys.argv[2])
prowk = int(sys.argv[3])
hash_type= sys.argv[4]
num_msg_limit = 10
num_confirmation_blocks = int(sys.argv[5])
qs = []
if debug:
    print("Opening queues, " , number_of_nodes)
for i in range(0, number_of_nodes):
    qs.append(Queue())

outputq = Queue()
msg_ct_q = Queue()
nodes= [Node(id,number_of_nodes,narry,prowk,hash_type,num_confirmation_blocks,num_msg_limit,msg_ct_list,debug) for id in range(0,number_of_nodes)]
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
    
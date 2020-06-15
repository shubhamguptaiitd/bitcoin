import hashlib

def get_hash(string):
    return hashlib.sha256(string.encode()).hexdigest()

def create_merkle_tree(list_of_items,narry=2):  ##  its a list of list of hashes
    leaves= list_of_items
    if len(leaves) % narry > 0:
        leaves = leaves + [leaves[-1]]*(narry-len(leaves) % narry)
    
    hashes_at_each_level = [leaves]
    len_current_level = len(leaves)
    i = 0
    while len_current_level > 1:
        slices = [hashes_at_each_level[i][index*narry:(index+1)*narry] for index in range(0, int(len_current_level/narry))]
        next_level_hashes = []
        for item in slices:
            next_level_hashes.append(get_hash("".join(item)))
        if len(next_level_hashes) > 1 and len(next_level_hashes) % narry > 0:
            next_level_hashes = next_level_hashes + [next_level_hashes[-1]]*(narry-len(next_level_hashes) % narry)
        hashes_at_each_level.append(next_level_hashes)
        len_current_level = len(next_level_hashes)
        i += 1

        #print(len_current_level)
    return hashes_at_each_level

def verify_transaction_given_merkle_tree_and_merkle_root(merkle_root_hash,merkle_tree,transaction,narry=2):
    if transaction not in merkle_tree[0]:
        return False
    leaves= merkle_tree[0]
    if len(leaves) % narry > 0:
        leaves = leaves + [leaves[-1]]*(narry-len(leaves) % narry)
    
    hashes_at_each_level = [leaves]
    len_current_level = len(leaves)
    i = 0
    while len_current_level > 1:
        #print("length of current label," ,len_current_level )
        slices = [hashes_at_each_level[i][index*narry:(index+1)*narry] for index in range(0, int(len_current_level/narry))]
        next_level_hashes = []
        for item in slices:
            next_level_hashes.append(get_hash("".join(item)))
        if len(next_level_hashes) > 1 and len(next_level_hashes) % narry > 0:
            next_level_hashes = next_level_hashes + [next_level_hashes[-1]]*(narry-len(next_level_hashes) % narry)
        hashes_at_each_level.append(next_level_hashes)
        len_current_level = len(next_level_hashes)
        if len(next_level_hashes) != len(merkle_tree[i+1]) or next_level_hashes != merkle_tree[i+1]:
            return False
        i += 1

    if merkle_tree[-1][0] != merkle_root_hash:
        return False
    return True


#verify_transaction_given_merkle_tree_and_merkle_root('6d58f77dd2518f27d24291b8df7850b656591a1a44c15ffa53d2b115e194f671',tp,'a',narry=3)#

#tp[2][0] = '64c7bb42344bc713ca924505af2c31e373e9f8c9084735f9a47503e65e8e8d05'

#tp = create_merkle_tree(['a','b','c','d','e','f','g','h','e','11','13','24'],3)
#print(tp)
    
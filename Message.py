class Message():
    def __init__(self,type,src,dst): 
        self.type = type  ##### Add to block, 
        self.src = src 
        self.dst = dst

    def __str__(self):
        return self.type + ":" + str(self.src) + "->" + str(self.dst) 


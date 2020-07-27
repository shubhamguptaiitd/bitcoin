class Message():
    def __init__(self,type,msg,src,dst): 
        self.type = type  ##### Add to block, 
        self.msg = msg
        self.src = src 
        self.dst = dst

    def __str__(self):
        return self.type + ":" + str(self.msg)+ "--" + str(self.src) + "->" + str(self.dst) 



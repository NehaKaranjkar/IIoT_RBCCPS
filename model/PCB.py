# PCB.py
#
#
# Author: Neha Karanjkar 
# Date: 18 Oct 2017


class PCB:
    def __init__(self, type_ID, serial_ID):

        #A PCB has the following attributes:
        self.type_ID=type_ID        # type (used to infer dimensions, num of components etc)
        self.serial_ID=serial_ID    # a unique identifier for each PCB instance

    def __str__(self):
        return"PCB <type_ID="+str(self.type_ID)+", serial_ID="+str(self.serial_ID)+">"



#A fixed-sized stack of PCBs.
#has parameters N(number of PCBs) and type_ID
class PCB_stack:
    stack=[]
    def __init__(self,type_ID,N):
        self.N=N
        self.type_ID=type_ID
        for i in range (N):
            self.stack.append(PCB(type_ID=type_ID,serial_ID=i))

    def __str__(self):
        return"PCB_stack <type_ID="+str(self.type_ID)+", size="+str(self.N)+">"


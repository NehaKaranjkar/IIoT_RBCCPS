# PCBBufferingModule.py
#
#   A machine that buffers PCBS at the output of the pick and place 
#   so that the buffered PCBs can be sent to the Reflow Oven in a burst.
#   The buffer has a fixed capacity.
#
#   The machine has two modes: "filling" and "emptying".
#   "filling" mode:-------------------
#       Initially the buffer is empty and in the "filling" mode.  
#       PCBs that  exit the pick and place machine are buffered 
#       in a Last-in-First out manner.
#   "emptying" mode:------------------
#       When the buffer is full, the state changes to "emptying" mode.
#       In this mode, no new items are placed in the buffer. The contents
#       of the buffer are pushed out to the conveyor belt one at a time.
#       The state changes back to "filling" mode when the buffer is full.
#
#   Parameters:
#       capacity: buffering capacity
#       
#   Author: Neha Karanjkar


import random,simpy,math
from PCB import *
from BaseOperator import BaseOperator

class PCBBufferingModule(BaseOperator):
    
    def __init__(self, env, name, inp, outp):
        BaseOperator.__init__(self,env,name)
        self.inp=inp
        self.outp=outp
        
        # parameters
        self.capacity=1
        self.buffer = None
        
        # states
        self.define_states(states=["filling", "emptying"], start_state="filling")
        self.process=env.process(self.behavior())
        
    
    def behavior(self):

        #checks:
        assert(isinstance(self.capacity,int) and self.capacity>1)
        
        #Initially the machine is in "filling" mode.
        self.change_state("filling")
        self.buffer=[]
        
        while True:

            if(self.current_state=="filling"):
                
                # wait at integer time instants until 
                # there's a PCB at the input
                pcb = None
                while(not pcb):
                    if self.inp.can_get():
                        pcb = yield self.inp.get()
                        break
                    else:
                        yield (self.env.timeout(1))
                
                # got a pcb.
                print("T=",self.env.now+0.0,self.name,"buffering a PCB",pcb)
                
                
                # push this PCB into a LIFO buffer.
                self.buffer.push(pcb)

                # check if the buffer is full.
                if(len(self.buffer)>=self.capacity):
                    self.change_state("emptying")
            
            
            if(self.current_state=="emptying"):
                
                # perform output at the middle of a time-slot
                yield (self.env.timeout(0.5))
                
                # wait until there's place at the output buffer
                while(True):
                    if self.outp.can_put():
                        yield self.outp.put(self.buffer.pop())
                        break
                    else:
                        yield (self.env.timeout(1))

                # managed to output a single PCB.
                print("T=",self.env.now+0.0,self.name,"output a single PCB",pcb)

                #check if the buffer is empty now.
                if(len(self.buffer)==0):
                    self.change_state("filling")

                # wait till an integer time instant
                yield (self.env.timeout(0.5))


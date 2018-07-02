# PCBBufferingModule.py
#
#   A machine that buffers PCBS at the output of the pick and place 
#   so that the buffered PCBs can be sent to the Reflow Oven in a burst.
#   The buffer has a fixed capacity_per_stage.
#
#   The machine has three modes: "bypass", "filling" and "emptying".
#   By default, the machine is in bypass mode. Buffering can be enabled
#   by calling the enable_buffering() function.
#
#   "bypass" mode:----------------------
#       In this mode, no buffering takes place. Items input
#       by the module are immediately sent to the output.
#       
#   "filling" mode:-------------------
#       Applicable only after enable_buffering() is called.
#       Initially the buffer is empty and in the "filling" mode.  
#       PCBs that  exit the pick and place machine are buffered 
#       in a Last-in-First out manner.
#   "emptying" mode:------------------
#       Applicable only after enable_buffering() is called.
#       When the buffer is full, the state changes to "emptying" mode.
#       In this mode, no new items are placed in the buffer. The contents
#       of the buffer are pushed out to the conveyor belt one at a time.
#       The state changes back to "filling" mode when the buffer is full.
#
#   Parameters:
#       capacity_per_stage: buffering capacity
#       
#   Author: Neha Karanjkar


import random,simpy,math
from PCB import *
from BaseOperator import BaseOperator
from ReflowOven import *
class PCBBufferingModule(BaseOperator):
    
    def __init__(self, env, name, inp, outp):
        BaseOperator.__init__(self,env,name)
        self.inp=inp
        self.outp=outp
        
        # parameters
        self.capacity_per_stage=1
        self.buffer = None
        
        # states
        self.define_states(states=["bypass","filling", "emptying"], start_state="bypass")
        self.process=env.process(self.behavior())

        # pointer to Reflow Oven for controlling it
        self.reflow_pointer = None

        # operational mode can be "BYPASS" or "BUFFERING_ENABLED"
        self.operational_mode = "BYPASS"
    
    def enable_buffering(self):
        self.operational_mode="BUFFERING_ENABLED"
        self.start_state="filling"

    def set_reflow_oven_control(self, RFO):
        self.reflow_pointer = RFO
        assert(isinstance(RFO, ReflowOven))
        self.reflow_pointer.set_external_control()
        

    def behavior(self):

        #checks:
        assert(isinstance(self.capacity_per_stage,int) and self.capacity_per_stage>1)
       
        #==============================
        #Behaviour in the BYPASS mode:
        #==============================
        if(self.operational_mode == "BYPASS"):
            self.change_state("bypass")
            while True:

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
                    print("T=",self.env.now+0.0,self.name,"input a PCB",pcb)
                    
                    # perform output at the middle of a time-slot
                    yield (self.env.timeout(0.5))
                    
                    # wait until there's place at the output buffer
                    while(True):
                        if self.outp.can_put():
                            yield self.outp.put(pcb)
                            break
                        else:
                            yield (self.env.timeout(1))

                    # output a single PCB.
                    print("T=",self.env.now+0.0,self.name,"output ",pcb,"to",self.outp)

                    # wait till an integer time instant
                    yield (self.env.timeout(0.5))

        #========================================
        #Behaviour in the BUFFERING_ENABLED mode:
        #=========================================
        else:
            #Initially the machine is in "filling" mode.
            self.change_state("filling")
            if(self.reflow_pointer!=None): self.reflow_pointer.turn_OFF()
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
                    self.buffer.append(pcb)

                    # check if the buffer is full.
                    if(len(self.buffer)>=self.capacity_per_stage):
                        self.change_state("emptying")
                        if(self.reflow_pointer!=None): self.reflow_pointer.turn_ON()
                
                
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
                    print("T=",self.env.now+0.0,self.name,"output ",pcb,"to",self.outp)

                    #check if the buffer is empty now.
                    if(len(self.buffer)==0):
                        self.change_state("filling")
                        if(self.reflow_pointer!=None): self.reflow_pointer.turn_OFF()

                    # wait till an integer time instant
                    yield (self.env.timeout(0.5))


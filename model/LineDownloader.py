# LineDownloader.py
#
# Collects PCBS one by one from the conveyor belt
# and loads them into a stack
#
# Parameters:
#   PCB_stack_size
#
# Author: Neha Karanjkar
# Date:   10 Nov 2017

import random,simpy
from PCB import *

class LineDownloader():
    
    def __init__(self, env, name, inp, outp):
        self.env=env
        self.name=name
        self.inp=inp
        self.outp=outp
        
        #default parameter values
        self.PCB_stack_size=10
        self.start_time = 0

        self.process=env.process(self.behavior())

    def behavior(self):
        
        yield (self.env.timeout(self.start_time))
        
        while True:
            
            pcb_stack=[]

            #collect enough PCBS to fill a stack
            while (len(pcb_stack) < self.PCB_stack_size):
                
                #wait and pick up a pcb from the conveyor belt
                while not self.inp.can_get():
                    yield self.env.timeout(1)

                pcb = yield self.inp.get()
                print("T=",self.env.now+0.0,self.name,"picked up",pcb,"from",self.inp)
                pcb_stack.append(pcb)

            
            #place the stack at the output
            yield self.outp.put(pcb_stack)
            print("T=",self.env.now+0.0,self.name,"placed stack on",self.outp)


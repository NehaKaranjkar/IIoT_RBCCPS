# Source.py
#
# A source creates a PCB stack of a given type after a certain delay,
# waits until the output buffer is free and then places the 
# stack at the output buffer.
#
# parameters:
#   delay
#   PCB_type
#   PCB_stack_size
#   
# Author: Neha Karanjkar
# Date:   19 Oct 2017


import random
import simpy

from PCB import *
from PCB_types import *


class Source():
    
    def __init__(self, env, name, outp):

        self.env=env
        self.name=name
        self.outp=outp
        
        #parameters, and default values
        self.delay=0
        self.PCB_type=1
        self.PCB_stack_size=1
        self.start_time=0
        
        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):
        
        assert(isinstance(self.start_time, int))
        assert(isinstance(self.delay, int))


        #wait until start time
        yield self.env.timeout(self.start_time)

        while(True):
            

            #create a stack of PCBs
            stack = []
            for i in range(self.PCB_stack_size):
                stack.append(PCB(type_ID=self.PCB_type, serial_ID=i, creation_timestamp=self.env.now))

            #place it at the output buffer
            yield self.outp.put(stack)

            print("T=", self.env.now+0.0, self.name,"output PCB stack to",self.outp)

            #delay
            yield (self.env.timeout(self.delay))


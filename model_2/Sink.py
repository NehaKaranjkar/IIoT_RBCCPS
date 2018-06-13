# Sink.py
#
# Consumes finished items as they arrive at its input buffer.
# 
# Author: Neha Karanjkar
# Date: 30 Oct 2017

import random
import simpy
from PCB import PCB

class Sink():
    def __init__(self, env, name, inp):
        self.env=env
        self.name=name
        self.inp=inp

        #default parameter values

        self.delay=0
        self.start_time=0.0
        
        #start behavior
        self.process=env.process(self.behavior())

        #count of the number of stacks completed and avg
        #time that each stack spent in the system
        self.num_items_finished=0.0
        self.average_cycle_time=0.0


    def behavior(self):
        
        yield self.env.timeout(self.start_time)
        
        while(True):
            
            #wait until there's a PCB at the input.
            pcb =yield self.inp.get()
            assert(isinstance(pcb,PCB))
            print("T=", self.env.now+0.0, self.name, "consumed a single PCB ",pcb,"from ",self.inp)
            PCB_cycle_time = self.env.now - pcb.creation_timestamp
            self.average_cycle_time = self.average_cycle_time * self.num_items_finished + PCB_cycle_time
            self.num_items_finished+=1
            self.average_cycle_time = self.average_cycle_time/self.num_items_finished

            
            #produce a delay
            yield self.env.timeout(self.delay)



# PickAndPlace.py
#
#  The PickAndPlace machine performs component placement one PCB at a time.
#  Each PCB consumes a certain number of components from the reels.
#  The time required to process a PCB is proportional
#  to the number of components in it
#   
#   Parameters:
#       delay: delay per component
#
#   Author: Neha Karanjkar
#   Date: 20 Oct 2017


import random,simpy,math
from PCB import *
from PCB_types import *

class PickAndPlace():
    def __init__(self, env, name, inp, outp):
        self.env=env
        self.name=name
        self.inp=inp
        self.outp=outp

        #default parameter values
        self.delay=0
        self.start_time=0

        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):

        # wait until start time
        yield (self.env.timeout(self.start_time))
        
        while True:
            
            # keep checking at integer time instants
            # until a PCB arrives at the input
            while (not self.inp.can_get()):
                yield (self.env.timeout(1))

            # pick up the PCB for processing
            pcb = self.inp.get_copy()
            print "T=",self.env.now+0.0,self.name,"started processing",pcb

            # infer parameters from the PCB's type. 
            num_components = get_PCB_num_components(pcb.type_ID)
            
            #start pick and place
            yield (self.env.timeout(self.delay*num_components))
            
            #wait until the next integer time instant
            yield (self.env.timeout(math.ceil(self.env.now) - self.env.now))
            print "T=",self.env.now+0.0,self.name,"finished processing",pcb
            
            # wait until there's place at the output
            # remove PCB from the input and 
            # place it at the output
            while (not self.outp.can_put()):
                yield (self.env.timeout(1))
            pcb = yield self.inp.get()
            yield self.outp.put(pcb)


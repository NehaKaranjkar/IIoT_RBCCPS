# BakingOven.py
#
# A baking oven waits until there is a stack
# of PCBs at it's input, then bakes the stack
# for 'delay' time and then places the stack 
# at its output. 
#
# parameters:
#   delay
#   
# Author: Neha Karanjkar
# Date:   10 Nov 2017


import simpy


class BakingOven():
    
    def __init__(self, env, name, inp, outp):

        self.env=env
        self.name=name
        self.inp=inp
        self.outp=outp
        
        #parameters, and default values
        self.delay=10
        self.start_time=0
        
        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):
        
        #wait until start time
        yield self.env.timeout(self.start_time)

        while(True):
            
            #wait until there's a stack at the input
            while not self.inp.can_get():
                yield (self.env.timeout(1))

            #start baking
            stack = self.inp.get_copy()
            print "T=", self.env.now+0.0, self.name,"picked up", stack,"from",self.inp

            #delay
            yield (self.env.timeout(self.delay))

            #pick it up from the input and place it at the output buffer
            stack = yield self.inp.get()
            yield self.outp.put(stack)

            print "T=", self.env.now+0.0, self.name,"output", stack,"to",self.outp

# Sink.py
#
# Consumes finished PCB stacks as they arrive.
# 
# Author: Neha Karanjkar
# Date: 30 Oct 2017

import random
import simpy


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

    def behavior(self):
        
        yield self.env.timeout(self.start_time)
        
        while(True):
            
            #wait until there's a stack at the input buffer

            stack=yield self.inp.get()
            print "T=", self.env.now+0.0, self.name, "consumed", stack,"from",self.inp
            
            #produce a delay
            yield self.env.timeout(self.delay)



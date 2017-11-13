# LineLoader.py
#
# Waits until there is a stack of PCB's at its input
# then picks up one PCB at a time from the stack 
# and places it on the conveyor belt.
#
#   parameters: 
#       delay: between picking up and placing each PCB
#
# Author: Neha Karanjkar
# Date:   19 Oct 2017

import random,simpy

class LineLoader():
    
    def __init__(self, env, name, inp, outp):
        self.env=env
        self.name=name
        self.inp=inp
        self.outp=outp

        self.delay=0
        self.start_time = 0

        self.process=env.process(self.behavior())

    def behavior(self):
        
        yield (self.env.timeout(self.start_time))

        while True:
            
            #wait until there's a job at the input
            pcb_stack=None
            
            while(not pcb_stack):
                if self.inp.can_get():
                    pcb_stack = self.inp.get_copy()
                    break
                else:
                    yield (self.env.timeout(1))
            
            #got a stack.
            print "T=",self.env.now+0.0,self.name,"started unloading",pcb_stack

            while pcb_stack.stack:
                
                #pick up a PCB from the stack
                pcb = pcb_stack.stack.pop()

                #delay
                yield (self.env.timeout(self.delay))
                
                # wait until there's place at the output
                while not self.outp.can_put():
                    yield (self.env.timeout(1))

                #place the PCB at the output
                yield self.outp.put(pcb)
                print "T=",self.env.now+0.0,self.name,"placed",pcb,"on",self.outp
            
            # Now remove the empty tray from the inp
            # so that the next job can arrive.
            s = yield self.inp.get()
                

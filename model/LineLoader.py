# LineLoader.py
#
# Waits until there is a stack of PCB's at its input
# then picks up one PCB at a time from the stack 
# and sends it to the next stage
#
#   parameters: 
#       delay: delay to pick and place each PCB
#
# Author: Neha Karanjkar
# Date:   19 Oct 2017

import random,simpy

class LineLoader():
    
    def __init__(self,env,name,input_buff,output_buff,delay):
        self.env=env
        self.name=name
        self.input_buff=input_buff
        self.output_buff=output_buff
        self.delay=delay
        self.process=env.process(self.behavior())

    def behavior(self):
        
        while True:
            #wait until there's a stack of PCBs at its input
            pcb_stack=yield self.input_buff.get()
            print "time=",self.env.now,self.name,"Started loading a new stack"

            while pcb_stack.stack:
                
                #pick up a PCB from the stack
                pcb = pcb_stack.stack.pop()
                #delay
                yield (self.env.timeout(self.delay))
                #place the PCB at the output
                #(wait until there's place at the output)
                yield self.output_buff.put(pcb)
                print "time=",self.env.now,self.name,"Placed",pcb,"on the line"



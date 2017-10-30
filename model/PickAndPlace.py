# PickAndPlace.py
#
#   The PickAndPlace machine waits until there is a PCB at its input,
#   then performs the component placement one PCB at a time.
#   Each PCB consumes a certain number of components from the reels
#   with a  fixed amount of delay per component.
#   
#   Parameters:
#       delay: delay per component
#
#   Author: Neha Karanjkar
#   Date: 20 Oct 2017

import random,simpy

class PickAndPlace():
    def __init__(self,env,name,input_buff,output_buff,delay):
        self.env=env
        self.name=name
        self.input_buff=input_buff
        self.output_buff=output_buff
        self.delay=delay

        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):

        while True:
            
            #wait until there's a PCB at its input
            pcb = yield self.input_buff.get()

            #start pick and place
            print "time=",self.env.now,self.name,"Started pick and place for",pcb
            yield (self.env.timeout(self.delay*pcb.num_components))

            #finished.
            print "time=",self.env.now,self.name,"Finished pick and place for",pcb,
            
            #place the PCB at the output
            #(wait until there's place at the output)
            yield self.output_buff.put(pcb)


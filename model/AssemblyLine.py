# AssemblyLine.py
#
# SimPy model of the SMT PCB manufacturing line
#
# Author: Neha Karanjkar
# Date:   19 Oct 2017


import random
import simpy

#Definition of PCB and PCB_stack classes
from PCB import *           

# Definitions of machines/operators in the assembly line
from LineLoader import *    
from ScreenPrinter import * 
from PickAndPlace import *
from HumanOperator import * 


#Source
#
#Places a stack of PCBs at the input
#of the LineLoader every once in a while
def Source(env,name,output_buff):
    for i in range(10):
        #produce a delay
        yield env.timeout(20)
        #create a stack of PCBs and place it at the output
        yield output_buff.put(PCB_stack(type_ID=1, N=10))
        print "time=",env.now,name,"placed a stack of PCBs at the input of LineLoader"

#Sink
#
#Consumes finished PCBs as they arrive
def Sink(env,input_buff):
    while(1):
        #produce a delay
        #yield env.timeout(random.randint(1,10))
        pcb=yield input_buff.get()
        print "time=",env.now,"Sink got",pcb


        
#Create an Environment and populate it:
env=simpy.Environment()

#buffers to model conveyor belts between stages
pcb_stack_buff=simpy.Store(env,capacity=1)
pcb_buff1=simpy.Store(env,capacity=1)
pcb_buff2=simpy.Store(env,capacity=1)
pcb_buff3=simpy.Store(env,capacity=3)
pcb_buff4=simpy.Store(env,capacity=1)

source=env.process(Source(env,"Bob",pcb_stack_buff)) #Source
lineloader=LineLoader(env,"LineLoader",pcb_stack_buff,pcb_buff1,delay=1) #LineLoader
screenprinter=ScreenPrinter(env,"ScreenPrinter",pcb_buff1,pcb_buff2,delay=10) #ScreenPrinter
pickandplace1=PickAndPlace(env,"PickAndPlace1",pcb_buff2,pcb_buff3,delay=1) #ScreenPrinter
pickandplace2=PickAndPlace(env,"PickAndPlace2",pcb_buff3,pcb_buff4,delay=1) #ScreenPrinter
sink=env.process(Sink(env,pcb_buff4))


#Human Operator
human1=env.process(HumanOperator(env,"Alice",screenprinter))
screenprinter.set_human_operator(human1)

#Run simulation
env.run(until=100)


# ScreenPrinter.py
#
#   The ScreenPrinter performs printing, one PCB at a time.
#   Each PCB consumes a certain amount of solder and adhesive
#   and incurs a certain amount of delay depending on the PCB's type_ID.
#   When the solder or adhesive levels falls below a certain threshold, 
#   a human operator is informed and the printing is paused 
#   until a refill is made by the operator.
#   
#   Parameters:
#       solder_capacity
#       adhesive_capacity
#       solder_initial_amount
#       adhesive_initial_amount
#       delay  (time to print a single PCB)
#
#
#   Author: Neha Karanjkar
#   Date: 19 Oct 2017

import random,simpy,math
from PCB import *
from PCB_types import *

class ScreenPrinter():
    def __init__(self,env,name,inp,outp):

        self.env=env
        self.name=name
        self.inp=inp
        self.outp=outp

        self.start_time=0
        self.human_operator=None
        
        # default parameter values:
        #
        # solder paste reserve
        self.solder_initial_amount=10
        self.solder_capacity=100
        #
        # adhesive reserve
        self.adhesive_initial_amount=10
        self.adhesive_capacity=100
        
        # create reserves
        self.solder_reserve = simpy.Container(env,init=self.solder_initial_amount, capacity=self.solder_capacity)
        self.adhesive_reserve=simpy.Container(env,init=self.adhesive_initial_amount, capacity=self.adhesive_capacity)
        # start behavior
        self.process=env.process(self.behavior())

    def set_human_operator(self,operator):
        # this is the operator we interrupt when the
        # solder/adhesive reserves are low.
        self.human_operator=operator
        
    def behavior(self):

        # check if the human operator has been assigned
        assert(self.human_operator)

        # wait until start time
        yield (self.env.timeout(self.start_time))

        while True:
            
            # keep checking at integer time instants
            # until a PCB arrives at the input
            while (not self.inp.can_get()):
                yield (self.env.timeout(1))

            # get the PCB
            pcb = self.inp.get_copy()
            print "T=",self.env.now+0.0,self.name,"started printing",pcb

            # infer printing parameters from the PCB's type. 
            solder_amt_required = get_PCB_solder_amt(pcb.type_ID)
            adhesive_amt_required = get_PCB_adhesive_amt(pcb.type_ID)
            
            # check if required amounts of solder/adhesive are present
            # If not, interrupt a human operator to start the refilling process.
            if(self.solder_reserve.level<solder_amt_required):
                print "T=",self.env.now+0.0,self.name,"WARNING: Solder reserve low!! Needs refilling."
                self.human_operator.interrupt("solder refill")
            
            if(self.adhesive_reserve.level<adhesive_amt_required):
                print "T=",self.env.now+0.0,self.name,"WARNING: Adhesive reserve low!! Needs refilling."
                self.human_operator.interrupt("adhesive refill")

            # wait until solder/adhesive have been refilled
            yield self.solder_reserve.get(solder_amt_required)
            yield self.adhesive_reserve.get(adhesive_amt_required)

            #wait until an integer time instant
            yield (self.env.timeout(math.ceil(self.env.now)-self.env.now))
            
            #print
            yield (self.env.timeout(self.delay))
            print "T=",self.env.now+0.0,self.name,"finished printing",pcb
            
            #Wait until there's place at the output,
            while (not self.outp.can_put()):
                yield (self.env.timeout(1))

            #remove the PCB from this stage and send it to the output
            yield self.inp.get()
            yield self.outp.put(pcb)
            print "T=",self.env.now+0.0,self.name,"output",pcb,"on",self.outp


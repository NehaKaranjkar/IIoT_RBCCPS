# ScreenPrinter.py
#
#   The ScreenPrinter waits until there is a PCB at its input,
#   then performs printing, one PCB at a time.
#   Each PCB consumes a certain amount of solder and adhesive
#   and incurs a certain amount of delay depending on the type of the PCB.
#   When the solder or adhesive levels falls below a certain threshold, 
#   a human operator is informed and the printing is paused 
#   until a refill is made by the operator.
#   
#   Parameters:
#       delay: delay for printing each PCB
#       solder_capacity
#       adhesive_capacity
#
#   Author: Neha Karanjkar
#   Date: 19 Oct 2017

import random,simpy

class ScreenPrinter():
    def __init__(self,env,name,input_buff,output_buff,delay):
        self.env=env
        self.name=name
        self.input_buff=input_buff
        self.output_buff=output_buff
        self.delay=delay

        #solder paste reserve
        solder_initial_reserve=20
        self.solder_capacity=100
        self.solder_reserve=simpy.Container(env,init=solder_initial_reserve,capacity=self.solder_capacity)

        #adhesive reserve
        adhesive_initial_reserve=8
        self.adhesive_capacity=100
        self.adhesive_reserve=simpy.Container(env,init=adhesive_initial_reserve,capacity=self.adhesive_capacity)


        #start behavior
        self.process=env.process(self.behavior())

    def set_human_operator(self,operator):
        #this is the operator we interrupt when the
        #solder/adhesive reserves are low.
        self.human_operator=operator
        


    def behavior(self):

        #check if human operator has been assigned
        assert(self.human_operator)

        while True:
            
            #wait until there's a PCB at its input
            pcb = yield self.input_buff.get()
            print "time=",self.env.now,self.name,"Started printing",pcb

            #check if required amount of solder is present
            solder_required=pcb.solder_amount_required
            if(self.solder_reserve.level<solder_required):
                print "time=",self.env.now,self.name,"WARNING: Solder reserve low!! Needs refilling."
                #Interrupt a human operator to start the refilling process.
                self.human_operator.interrupt("solder refill")
            
            #check if required amount of adhesive is present
            adhesive_required=pcb.adhesive_amount_required
            if(self.adhesive_reserve.level<adhesive_required):
                print "time=",self.env.now,self.name,"WARNING: Adhesive reserve low!! Needs refilling."
                #Interrupt a human operator to start the refilling process.
                self.human_operator.interrupt("adhesive refill")


            #start printing
            yield self.solder_reserve.get(solder_required)
            yield self.adhesive_reserve.get(adhesive_required)
            yield (self.env.timeout(self.delay))
            print "time=",self.env.now,self.name,"Finished printing",pcb,
            print "Consumed", solder_required,"units of solder and",adhesive_required,"units of adhesive"
            
            #place the PCB at the output
            #(wait until there's place at the output)
            yield self.output_buff.put(pcb)


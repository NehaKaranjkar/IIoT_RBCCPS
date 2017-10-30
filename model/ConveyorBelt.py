# ConveyorBelt.py
# 
# This conveyor belt is modeled like a shift-register.
# The number of stages and delay per stage are parameters.
# Each stage corresponds to a place-holder for a single job.
# The conveyor belt moves (akin to a shift-right operation)
# after each 'delay' amount of time.
#
# If the object in the last stage of the conveyor belt is
# not picked up, the belt stalls.
# 
#   Author: Neha Karanjkar
#   Date: 27 Oct 2017

import random,simpy


class ConveyorBelt():
    def __init__(self,env,name,num_stages,delay):
        self.env=env
        self.name=name
        self.delay=delay
        self.num_stages=num_stages
        
        #input and output buffers
        self.input_buf=simpy.Store(env,capacity=1)
        self.output_buf=simpy.Store(env,capacity=1)

        assert(isinstance(num_stages,int))
        assert(num_stages>=2)

        #list to model stages
        self.stages=[None for i in range(num_stages)]

        #start behavior
        self.process=env.process(self.behavior())
        self.process=env.process(self.monitor())
    
    def print_state(self):
        print "|",
        if(len(self.input_buf.items)!=0):
            print self.input_buf.items[0],
        else:
            print None,
        print "|",
        for i in range(1,self.num_stages-1):
            print self.stages[i],"|",
        if(len(self.output_buf.items)!=0):
            print self.output_buf.items[0],
        else:
            print None,
        print "|",

        print ""
        

    def monitor(self):

        #small offset
        yield (self.env.timeout(0.1))

        while True:
            self.print_state()
            #delay
            yield (self.env.timeout(self.delay))



    def behavior(self):

        while True:
            #delay
            yield (self.env.timeout(self.delay))

            #if output_buf is empty, shift-right
            #the contents of the belt.
            if(len(self.output_buf.items)==0):
                               
                #pick up the object from input_buf if present
                if(len(self.input_buf.items)==0):
                    obj=None
                else:
                    obj=yield self.input_buf.get()
                
                self.stages[0]=obj
            
                #shift right
                self.stages = [None] + self.stages[0:-1]

                #put the last object in output_buf
                obj=self.stages[-1]
                if(obj!=None):
                    yield self.output_buf.put(self.stages[-1])
                print "Conveyor belt moved to the right at time",env.now
            


class Sender():
    def __init__(self,env,delay,output_buf):
        self.env=env
        self.delay=delay
        
        #pointer to output buffer
        self.output_buf=output_buf

        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):
        
        count=0
        while True:
            
            #delay
            yield (self.env.timeout(self.delay))

            #try to place an object in the output buf if its empty
            if(len(self.output_buf.items)==0):
                obj = "*_"+str(count)
                yield self.output_buf.put(obj)
                count+=1
                print "Sender placed", obj,"on conveyor belt at time", env.now


class Receiver():
    def __init__(self,env,input_buf):
        self.env=env
        
        #pointer to input buffer
        self.input_buf = input_buf

        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):
        
        while True:
            #random delay
            yield (env.timeout(1+random.randint(1,4)))
            
            #try to input an object from the buffer
            obj = yield self.input_buf.get()
            print "Receiver picked up", obj,"from conveyor belt at time", env.now

env=simpy.Environment()
conveyor_belt=ConveyorBelt(env, name="ConveyorBelt", num_stages=2, delay=2)
sender = Sender(env, delay=1, output_buf=conveyor_belt.input_buf)
receiver = Receiver(env, input_buf = conveyor_belt.output_buf)

env.run(until=100)

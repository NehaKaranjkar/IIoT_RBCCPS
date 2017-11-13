# HumanLoader:
#
# The human loader keeps checking
# if jobs are available in a given list
# of input buffers, and places them
# as they arrive at the input of the line loader.
#
# parameters:
#   delay:  time between picking up a job and 
#           placing it near the line loader.
#   
# Author: Neha Karanjkar
# Date:   10 Nov 2017


import simpy,random


class HumanLoader():
    
    def __init__(self, env, name, inp_list, outp):

        self.env=env
        self.name=name
        self.inp_list=inp_list
        self.outp=outp
        
        #parameters, and default values
        self.delay=0
        self.start_time=0
        
        #start behavior
        self.process=env.process(self.behavior())

    def behavior(self):
        
        #wait until start time
        yield self.env.timeout(self.start_time)

        while(True):
            
            #keep checking the input buffers
            #to see if one of them contains a job
            stack = None
            p=0
            while (not stack):
                
                #randomly shuffle the elements in inp_list
                # to give each input equal priority 
                random.shuffle(self.inp_list)

                for inp in self.inp_list:
                    if inp.can_get():
                        stack = yield inp.get()
                        p=inp
                        break
                if not stack:   
                    yield self.env.timeout(1)
            
            #got a stack 
            print "T=", self.env.now+0.0, self.name,"picked up",stack,"from",p

            #delay
            yield (self.env.timeout(self.delay))

            #place it at the output buffer
            yield self.outp.put(stack)
            print "T=", self.env.now+0.0, self.name,"placed",stack,"at",self.outp


# HumanOperator.py
#
# A human operator can be assigned several tasks.
# The operator maintains a list of the tasks assigned,
# the machine on which it is to be performed. 
#
# The operator performs the appropriate task
# whenever interrupted.
#
# Author: Neha Karanjkar
# Date:   20 Nov 2017


import random
import simpy

# Information about an assigned task
# is stored as a tuple:
from collections import namedtuple
Task = namedtuple('Task', 'task_name machine_name task_ptr machine_ptr delay')


class HumanOperator():
    
    def __init__(self, env, name):
        self.env=env
        self.name=name
        
        # list of tasks assigned 
        # to this operator
        self.task_list=[]
        
        # start behavior
        self.behavior=env.process(self.behavior())

        #state (idle/busy)
        self.state = "idle"

        #stats:
        self.idle_time=0.0
        self.busy_time=0.0

    
    # function to assign a new task
    # to this operator
    def assign_task(self, task_name, machine_name, task_ptr, machine_ptr, delay):
        
        self.task_list.append(Task(task_name, machine_name, task_ptr, machine_ptr, delay))


    
    def behavior(self):

        # stay idle until interrupted by a machine.
        # when interrupted, perform the assigned task
        # and resume idle state

        while True:

            try:
                self.state = "idle" 
                # wait for some arbitrary time
                # until interrupted
                yield self.env.timeout(10)

            except simpy.Interrupt as i:
                
                machine_name, cause = i.cause.split(":")
                print "T=",self.env.now,self.name,"was interrupted by",machine_name,"for",cause

                
                # check if thereis one and *only one* task
                # that has been assigned to me and matches this criteria:
                task = [t for t in self.task_list if ( t.task_name==cause and t.machine_name==machine_name )]
                if len(task)==0:
                    print"ERROR!! no such task assigned to operator",self.name
                assert(len(task)==1)
                task=task[0]

                
                #perform the task
                print "T=",self.env.now,self.name,"starting task",cause
                yield self.env.timeout(task.delay)
                
                task.task_ptr(machine=task.machine_ptr)
                print "T=",self.env.now,self.name,"finished task",cause


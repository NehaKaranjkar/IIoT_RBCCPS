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
Task  = namedtuple('Task', 'task_name machine_name task_ptr machine_ptr delay')


class HumanOperator():
    
    def __init__(self, env, name):
        self.env=env
        self.name=name
        
        # list of tasks assigned 
        # to this operator
        self.task_list=[]
        
        # start behavior
        self.behavior=env.process(self.behavior())


        #stats collection:
        self.states = ["idle","busy"]
        self.states_time_spent = [0.0 for s in self.states]
        self.current_state = "idle" # current state
        self.timestamp = 0.0 # time instant at which the last state change occured.


    
    # function to assign a new task
    # to this operator
    def assign_task(self, task_name, machine_name, task_ptr, machine_ptr, delay):
        
        self.task_list.append(Task(task_name, machine_name, task_ptr, machine_ptr, delay))
  

    # record time spent in the current state 
    # since the last timestamp
    def update_stats(self):
        i = self.states.index(self.current_state)
        self.states_time_spent[i] += self.env.now - self.timestamp
    
    # change state
    def change_state(self, new_state):
        self.update_stats()
        self.current_state = new_state
        self.timestamp=self.env.now


    # print usage statistics
    def print_stats(self):
        
        self.update_stats()
        total_time = sum(self.states_time_spent)
        assert (total_time>0)
        print self.name,":",
        for i in range(len(self.states)):
            print self.states[i], "=",
            t = self.states_time_spent[i]
            t_percent = self.states_time_spent[i]/total_time*100.0
            print t,"({0:.2f}".format(t_percent)+"%)",
        print ""
            
        
      
    def behavior(self):
        
        self.change_state("idle")
        # stay idle until interrupted by a machine.
        # when interrupted, perform the assigned task
        # and resume idle state
        while True:

            try:
                # wait for some arbitrary time
                # until interrupted
                yield self.env.timeout(10)

            except simpy.Interrupt as i:
                
                self.change_state("busy")
                            
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

                self.change_state("idle")


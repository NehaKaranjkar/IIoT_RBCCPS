# HumanOperator.py
#
# The human operator is usually busy with some task.
# when interrupted, he/she refills the solder/adhesive
# in the ScreenPrinter machine.
#
# Author: Neha Karanjkar
# Date:   19 Oct 2017


import random
import simpy

def HumanOperator(env, name, ScreenPrinterMachine):

    while True:
        print "time=",env.now,name,"Started a low priority task."
        task_total_time=random.randint(50,60)
        task_remaining_time=task_total_time

        while(task_remaining_time>0):
            task_start_time=env.now
            try:
                yield env.timeout(task_remaining_time)

            except simpy.Interrupt as i:
                print "time=",env.now,name,"was interrupted for ",i.cause

                #calculate remaining time for the task at hand
                task_remaining_time = task_remaining_time - (env.now-task_start_time)

                #refill the solder reserve
                if(i.cause=="solder refill"):
                    print "time=",env.now,name,"Started solder refill."
                    yield env.timeout(5)
                    refill_amount=ScreenPrinterMachine.solder_capacity-ScreenPrinterMachine.solder_reserve.level
                    ScreenPrinterMachine.solder_reserve.put(refill_amount)
                
                #refill the adhesive reserve
                if(i.cause=="adhesive refill"):
                    print "time=",env.now,name,"Started adhesive refill."
                    yield env.timeout(5)
                    refill_amount=ScreenPrinterMachine.adhesive_capacity-ScreenPrinterMachine.adhesive_reserve.level
                    ScreenPrinterMachine.adhesive_reserve.put(refill_amount)

                #complete the remaining task
                if(task_remaining_time>0):
                    print "time=",env.now,name,"Resumed low priority task."
        
        print "time=",env.now,name,"Finished low priority task."




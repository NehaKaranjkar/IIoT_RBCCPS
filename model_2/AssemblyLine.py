# AssemblyLine.py
#
# SimPy model of an SMT PCB assembly line.
# See ./documentation for an illustration of the line. 
# The system consists of a set of machines
# connected over conveyor belts in a sequence.
#
#
# Author: Neha Karanjkar

import random
import simpy



# Create an Environment:
env=simpy.Environment()


#===============================================
# Instantiate machines, set their parameters
#and connect them using conveyor belts/buffers
#===============================================

# PCB definitions:
from PCB import *           


# Instantiate buffers.
# Succesive machines in the assembly line are connected
# using buffers. One machine can "put" and the next machine 
# can "get"  a PCB from the buffer.
from Buffer import *
buff = []
NUM_BUFFERS = 6
for i in range (NUM_BUFFERS):
    buff.append(Buffer(env, name="buff_"+str(i), capacity=1))


# Instantiate conveyor belts
# the first conveyor belt is between the screen printer to the Pick and place1.
# the second belt is between the Pick and place2 and the Reflow Oven.
from ConveyorBelt import *
belt_SP_to_PP1 = ConveyorBelt(env=env, name="belt_SP_to_PP1", num_stages=3, delay_per_stage=1)
belt_PP2_to_RFO = ConveyorBelt(env=env, name="belt_PP2_to_RFO", num_stages=3, delay_per_stage=1)


# Instantiate Human Operators.
# Human operators can be interrupted by machine
# for performing tasks such as refilling machine consummables.
from HumanOperator import *
human_operator_1 = HumanOperator (env=env, name="human_operator_1")
human_operator_2 = HumanOperator (env=env, name="human_operator_2")

#======================================
# Machines in the assembly Line:
#======================================
#
#======================================
# Source:
#======================================
# A source creates a PCB stack of a given type 
# periodically after a certain delay, 
# and places the stack at its output.
# The source stalls if there's no place at the output.
from Source import *
source_1  = Source (env=env, name="source_1", outp=buff[0])
source_1.delay = 0
source_1.PCB_type = 1
source_1.PCB_stack_size=10


#======================================
# LineLoader:
#======================================
# A line loader waits until there is a stack of PCBs
# at its input. Then, it picks up PCBs from the stack
# one at a time and places them on the conveyor belt.
# parameters: 
#   delay (for pushing a single PCB into the empty output buffer)
from LineLoader import *
line_loader      = LineLoader (env=env, name="line_loader", inp=buff[0], outp=buff[1])
line_loader.delay= 9

#======================================
# ScreenPrinter:
#======================================
#   The ScreenPrinter performs printing, one PCB at a time.
#   Each PCB consumes a certain amount of solder and adhesive
#   and incurs a certain amount of delay.
#   When the solder or adhesive levels falls below a certain threshold, 
#   a human operator is informed and the printing is paused 
#   until a refill is made by the operator.
#   After every 'n' printing operations, a 'cleaning' operation
#   is automatically performed. The value of n is the parameter 'num_pcbs_per_cleaning'
#   Each cleaning takes up a certain time specified as 'cleaning_delay'.
from ScreenPrinter import *
screen_printer   = ScreenPrinter (env=env, name="screen_printer", inp=buff[1], outp=belt_SP_to_PP1)

screen_printer.solder_capacity=500 # units: gram
screen_printer.solder_initial_amount=500

screen_printer.adhesive_capacity=500
screen_printer.adhesive_initial_amount=500

screen_printer.printing_delay=18
screen_printer.cleaning_delay=28
screen_printer.num_pcbs_per_cleaning=2

#  power ratings (in watts) for each state
# states: ["idle","waiting_for_refill","printing","cleaning","waiting_to_output"]
screen_printer.set_power_ratings([100.0, 100.0, 500.0, 1000.0, 100.0])


#======================================
# PickAndPlace:
#======================================
#  The PickAndPlace machine performs component placement one PCB at a time.
#  The processing for each PCB incurs a certain delay.
#  After a randomly distributed interval, a reel replacement operation is necessary
#  and a human operator is interrupted to perform the replacement.
from PickAndPlace import *
pick_and_place_1 = PickAndPlace (env=env, name="pick_and_place_1", inp=belt_SP_to_PP1, outp=buff[2] )
pick_and_place_2 = PickAndPlace (env=env, name="pick_and_place_2", inp=buff[2], outp=belt_PP2_to_RFO)
pick_and_place_1.processing_delay=85
pick_and_place_2.processing_delay=50
# num of PCBs processed after which reel replacement is required
pick_and_place_1.reel_replacement_interval = 20
pick_and_place_2.reel_replacement_interval = 10
#  power ratings (in watts) for each state
# states: ["idle","waiting_for_reel_replacement","processing","waiting_to_output"]
pick_and_place_1.set_power_ratings([100.0, 100.0, 500.0, 100.0])
pick_and_place_2.set_power_ratings([100.0, 100.0, 500.0, 100.0])


#======================================
# PCB Buffering module:
#======================================
from PCBBufferingModule import *
buffering_module = PCBBufferingModule (env=env, name="buffering_module", inp=belt_PP2_to_RFO, outp=buff[3] )
reflow_oven.num_stages = 6
reflow_oven.delay_per_stage=10
reflow_oven.setup_time=120 # setup time is 20 minutes=120 seconds.

#  power ratings (in watts) for each state
# states: ["off", "setup", "temperature_maintain_unoccupied", "temperature_maintain_occupied"]
reflow_oven.set_power_ratings([320.0, 33000.0, 25800.0, 25800.0])

#======================================
# Reflow Oven:
#======================================
#  The Reflow Oven is similar to a conveyor belt.
from ReflowOven import *
reflow_oven = ReflowOven (env=env, name="reflow_oven", inp=belt_PP2_to_RFO, outp=buff[3] )
reflow_oven.num_stages = 6
reflow_oven.delay_per_stage=10
reflow_oven.setup_time=120 # setup time is 20 minutes=120 seconds.

#  power ratings (in watts) for each state
# states: ["off", "setup", "temperature_maintain_unoccupied", "temperature_maintain_occupied"]
reflow_oven.set_power_ratings([320.0, 33000.0, 25800.0, 25800.0])

#======================================
# Sink:
#======================================
# A sink consumes PCBs or PCB stacks from its input buffer
# and maintains a count of total PCBs consumed and the average
# cycle time for each PCB
from Sink import *
sink_1             = Sink (env=env, name="sink_1", inp=buff[3])
sink_1.delay = 0

#======================================
# Assignment of Tasks to Human Operators:
#======================================
# Assign some human operators to 
# handle refilling tasks in the screen printer and pick and place machines.
# A human operator remains idle until interrupted
# by a machine and then performs the assigned task.

# operator 1: 
screen_printer.set_refill_operator(human_operator_1)
human_operator_1.assign_task(task_name="solder_refill",machine_name="screen_printer", task_ptr=solder_refill_task, machine_ptr=screen_printer, delay=10)
human_operator_1.assign_task(task_name="adhesive_refill",machine_name="screen_printer", task_ptr=adhesive_refill_task, machine_ptr=screen_printer, delay=10)

pick_and_place_1.set_reel_replacement_operator(human_operator_1)
pick_and_place_2.set_reel_replacement_operator(human_operator_1)
human_operator_1.assign_task(task_name="reel_replacement",machine_name="pick_and_place_1", task_ptr=reel_replacement_task, machine_ptr=pick_and_place_1, delay=10)
human_operator_1.assign_task(task_name="reel_replacement",machine_name="pick_and_place_2", task_ptr=reel_replacement_task, machine_ptr=pick_and_place_2, delay=10)



# Run simulation, 
T =3600*8
print("Running simulation for", T," seconds")


#print the activity log to a file.
import sys 
import datetime

original_stdout = sys.stdout
activity_log_file = open("activity_log.txt","w")
sys.stdout = activity_log_file

current_time = datetime.datetime.now()
current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
print("Activity Log generated on ",current_time_str)
env.run(until=T)
sys.stdout = original_stdout

print("Activity log generated in file: activity_log.txt")

# Print usage statistics:
print("\n================================")
print("Stats:")
print("================================")
print ("Total time elapsed = ",env.now," seconds")
print ("Total number of PCBs processed =",sink_1.num_items_finished)
print ("Average cycle-time per PCB = %0.2f" %round(sink_1.average_cycle_time), "seconds")
print ("Average throughput = ",sink_1.num_items_finished/float(env.now)*3600," PCBs per hour.")

machines = [line_loader, screen_printer, belt_SP_to_PP1, pick_and_place_1, pick_and_place_2, belt_PP2_to_RFO, reflow_oven]
machines_e = [screen_printer, pick_and_place_1, pick_and_place_2, reflow_oven]
humans = [human_operator_1,human_operator_2]

print("\n================================")
print("Utilization Report: ")
print("================================")
for i in machines:
    i.print_utilization()
for i in humans:
    i.print_utilization()

print("\n================================")
print("Energy Consumption: ")
print("================================")
total_energy=0.0
for i in machines_e:
    i.print_energy_consumption()
    total_energy+=sum(i.get_energy_consumption())
print("Total energy consumed = ",total_energy/1e3, "Kilo Joules")
print ("Average energy consumed per-PCB = ",total_energy/(float(sink_1.num_items_finished)*1e3)," Kilo Joules per PCB.")


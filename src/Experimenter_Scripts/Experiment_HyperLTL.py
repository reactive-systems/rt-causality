import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import cause_checker as cc
import pyuppaal as pyu
import ta_structs as ta
import trace_structs as ts
import time

top = parent = os.path.dirname(parent)
sys.path.append(top)

from causality_tool import set_verifyta_path_main

set_verifyta_path_main()

sample_size = 2

ta_path = os.path.join(os.path.dirname(__file__).removesuffix("\\src\\Experimenter_Scripts"), 'Thesis_Examples\\HyperLTL_Example\\HyperLTL_TA.xml')
trace_path = os.path.join(os.path.dirname(__file__).removesuffix("\\src\\Experimenter_Scripts"), 'Thesis_Examples\\HyperLTL_Example\\HyperLTL_Trace_Lasso.txt')

print("Reading the following TA file: ", ta_path)
timed_automaton = ta.System(pyu.UModel(ta_path))

print("Reading the following trace file: ", trace_path)
trace = ts.parse_trace_from_file(trace_path)

bf_cause_checker = cc.CauseChecker(timed_automaton, trace, ts.DelayCause([], [("hi2!", 2), ("hi2!", 4)]))
act_cause_checker = cc.CauseChecker(timed_automaton, trace, ts.DelayCause([], [("hi2!", 2)]))
cause_computer = cc.CauseComputer(timed_automaton, trace)

causeBF_time = 0
causeBF_MIN_time = 0
causeAct_time = 0

but_for_causes_time = 0
actual_causes_time = 0

for i in range(sample_size):

    start = time.time()
    bf_cause_checker.check_But_For_Cause()
    end = time.time()
    causeBF_time += end - start

    start = time.time()
    bf_cause_checker.check_Min_But_For_Cause()
    end = time.time()
    causeBF_MIN_time += end - start

    start = time.time()
    act_cause_checker.check_Min_But_For_Cause()
    end = time.time()
    causeAct_time += end - start

    start = time.time()
    but_for_causes = cause_computer.compute_But_For_Cause()
    end = time.time()
    but_for_causes_time += end - start

    start = time.time()
    actual_causes = cause_computer.compute_Actual_Cause()
    end = time.time()
    actual_causes_time += end - start

res = "Runtime Results HyperLTL, Sample Size: " + str(sample_size)
res += "\n\nBut-For Cause Checking, Runtime: " + str(causeBF_time / sample_size)
res += "\nMinimal But-For Cause Checking, Runtime: " + str(causeBF_MIN_time / sample_size)
res += "\nActual Cause Checking, Runtime: " + str(causeAct_time / sample_size )
res += "\nBut-For Cause Computation, Runtime: " + str(but_for_causes_time / sample_size)
res += "\nActual Cause Computation, Runtime: " + str(actual_causes_time / sample_size )

print (res)

with open("src\\Experimenter_Scripts\\HyperLTL_Results.txt", "w") as file:
    file.write(res)

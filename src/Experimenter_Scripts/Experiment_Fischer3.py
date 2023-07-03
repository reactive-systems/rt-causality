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

ta_path = os.path.join(os.path.dirname(__file__).removesuffix("\\src\\Experimenter_Scripts"), 'Thesis_Examples\\Fischer\\Fischer_TA.xml')
trace_path = os.path.join(os.path.dirname(__file__).removesuffix("\\src\\Experimenter_Scripts"), 'Thesis_Examples\\Fischer\\Fischer_Trace1.txt')

print("Reading the following TA file: ", ta_path)
timed_automaton = ta.System(pyu.UModel(ta_path))

print("Reading the following trace file: ", trace_path)
trace = ts.parse_trace_from_file(trace_path)

cause_checker2 = cc.CauseChecker(timed_automaton, trace, ts.DelayCause([(1, 3)], [("tau_1!", 1)]))
cause_checker3 = cc.CauseChecker(timed_automaton, trace, ts.DelayCause([], [("tau_2!", 3), ("tau_1!", 4),  ("tau_1!", 5)]))
cause_checker4 = cc.CauseChecker(timed_automaton, trace, ts.DelayCause([(8, 5), (1, 7)], [("tau_1!", 4), ("tau_1!", 5)]))
cause_computer = cc.CauseComputer(timed_automaton, trace)

cause3_time = 0
mincause2_time = 0
mincause3_time = 0
mincause4_time = 0

actcause2_time = 0
actcause3_time = 0
actcause4_time = 0

but_for_causes_time = 0
actual_causes_time = 0

for i in range(sample_size):

    start = time.time()
    cause_checker3.check_But_For_Cause()
    end = time.time()
    cause3_time += end - start

    start = time.time()
    cause_checker2.check_Min_But_For_Cause()
    end = time.time()
    mincause2_time += end - start

    start = time.time()
    cause_checker3.check_Min_But_For_Cause()
    end = time.time()
    mincause3_time += end - start

    start = time.time()
    cause_checker4.check_Min_But_For_Cause()
    end = time.time()
    mincause4_time += end - start

    start = time.time()
    cause_checker2.check_Actual_Cause()
    end = time.time()
    actcause2_time += end - start

    start = time.time()
    cause_checker3.check_Actual_Cause()
    end = time.time()
    actcause3_time += end - start

    start = time.time()
    cause_checker4.check_Actual_Cause()
    end = time.time()
    actcause4_time += end - start

    start = time.time()
    but_for_causes = cause_computer.compute_But_For_Cause()
    end = time.time()
    but_for_causes_time += end - start

    start = time.time()
  #  actual_causes = cause_computer.compute_Actual_Cause()
    end = time.time()
    actual_causes_time += end - start

res = "Runtime Results Fischer, Trace 3, Sample Size: " + str(sample_size)
res += "But-For Cause3 Checking, Runtime: " + str(cause3_time / sample_size)
res += "\nMin But-For Cause 2 Checking, Runtime: " + str( mincause2_time / sample_size )
res += "\nMin But-For Cause 3 Checking, Runtime: " + str( mincause3_time / sample_size )
res += "\nMin But-For Cause 4 Checking, Runtime: " + str(mincause4_time / sample_size )
res += "\nActual Cause 2 Checking, Runtime: " + str(actcause2_time / sample_size )
res += "\nActual Cause 3 Checking, Runtime: " + str(actcause3_time / sample_size )
res += "\nActual Cause 4 Checking, Runtime: " + str(actcause4_time / sample_size )
res += "\nBut-For Cause Computation, Runtime: " + str(but_for_causes_time / sample_size)
res += "\nActual Cause Computation, Runtime: " + str(actual_causes_time / sample_size )

print (res)

with open("src\\Experimenter_Scripts\\Fischer_Results_Trace3.txt", "w") as file:
    file.write(res)

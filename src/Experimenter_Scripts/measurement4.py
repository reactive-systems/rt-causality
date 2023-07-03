import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import experimenter as exp
import pyuppaal as pyu


top = parent = os.path.dirname(parent)
sys.path.append(top)

from causality_tool import set_verifyta_path_main

set_verifyta_path_main()

sample_size = 1
ta_length = [30]#[5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
cause_size = [2]

res_SAT = "SAT Check:\n"
res_CF_BF = "CF-BF Check:\n"
res_CF_Act = "CF-Act Check:\n"

# Dummy Check to prevent starting issues:

experimenter = exp.Experimenter_Checking(2, 2, 2, 2)
experimenter.experiment_BF_Cause()
experimenter.experiment_Min_BF_Cause()
experimenter.experiment_Actual_Cause()

for t in ta_length:
    if t > 0:
        continue
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_SAT()

    res_SAT += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

for t in ta_length:
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_CF_BF() #Change causality notion here

    res_CF_BF += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

for t in ta_length:
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_CF_Act() #Change causality notion here

    res_CF_Act += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

res = "\nMeasurements Results: \n\n" + "Sample size:" + str(sample_size) + "\nCause sizes: " + str(cause_size) + "\n\n"
res += res_SAT + "\n" + res_CF_BF + "\n" + res_CF_Act + "\n"

print(res)
with open("src\\Experimenter_Scripts\\Measurement4_Results.txt", "w") as file:
    file.write(res)

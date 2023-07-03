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

sample_size = 10
ta_length = [100]
cause_size = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]

res_SAT = "SAT-Condition:\n"
res_CF_BF = "CF-BF Condition:\n"

# Dummy Check to prevent starting issues:

experimenter = exp.Experimenter_Checking(2, 2, 2, 2)
experimenter.experiment_BF_Cause()
experimenter.experiment_Min_BF_Cause()
experimenter.experiment_Actual_Cause()


for t in ta_length:
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time = experimenter.experiment_SAT()
        res_SAT += "t = r = " + str(t) + ", c = " + str(c) +" --> Time: " + str(time) + "\n"

for t in ta_length:
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time = experimenter.experiment_CF_BF()
        res_CF_BF += "t = r = " + str(t) + ", c = " + str(c) +" --> Time: " + str(time) + "\n"

res = "\nMeasurements Results: \n\n" + "Sample size:" + str(sample_size) + "\n\n"
res += res_SAT + "\n" + res_CF_BF + "\n"

print(res)

with open("src\\Experimenter_Scripts\\Measurement2_Results.txt", "w") as file:
    file.write(res)

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

sample_size = 2
ta_length = [2]
cause_size = [2]

res_BF = "But-For Causality:\n"
res_BF_MIN = "Minimal But-For Causality:\n"
res_Act = "Actual Causality:\n"

# Dummy Check to prevent starting issues:

experimenter = exp.Experimenter_Checking(2, 2, 2, 2)
experimenter.experiment_BF_Cause()
experimenter.experiment_Min_BF_Cause()
experimenter.experiment_Actual_Cause()

for t in ta_length:
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_BF_Cause()

    res_BF += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

for t in ta_length:
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_Min_BF_Cause() #Change causality notion here

    res_BF_MIN += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

for t in ta_length:
    if t > 25:
        continue
    time = 0
    for c in cause_size:
        experimenter = exp.Experimenter_Checking(sample_size, t, t, c)
        time += experimenter.experiment_Actual_Cause() #Change causality notion here

    res_Act += "t = r = " + str(t) + " --> Time: " + str(time / len(cause_size)) + "\n"

res = "\nMeasurements Results: \n\n" + "Sample size:" + str(sample_size) + "\nCause sizes: " + str(cause_size) + "\n\n"
res += res_BF + "\n" + res_BF_MIN + "\n" + res_Act + "\n"

print(res)
with open("src\\Experimenter_Scripts\\Measurement3_Results.txt", "w") as file:
    file.write(res)

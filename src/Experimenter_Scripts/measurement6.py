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
ta_length = [2]
cause_size = [2]

res_BF = "But-For Causality:\n"
res_Act = "Actual Causality:\n"

# Dummy Computation to prevent starting issues:

experimenter = exp.Experimenter_Computation(2, 2, 2, 2)
experimenter.experiment_BF_Cause()
experimenter.experiment_Actual_Cause()

for t in ta_length:
    for c in cause_size:
        if c > 2 * t:
            continue
        experimenter = exp.Experimenter_Computation(sample_size, t, t, c)
        time = experimenter.experiment_BF_Cause()
        res_BF += "t = r = " + str(t) + ", c = " + str(c) +" --> Time: " + str(time) + "\n"


for t in ta_length:
    for c in cause_size:
        if c > 2 * t:
            continue
        experimenter = exp.Experimenter_Computation(sample_size, t, t, c)
        time = experimenter.experiment_Actual_Cause()
        res_Act += "t = r = " + str(t) + ", c = " + str(c) +" --> Time: " + str(time) + "\n"

res = "\nMeasurements Results: \n\n" + "Sample size:" + str(sample_size) + "\n\n"
res += res_BF + "\n" + res_Act + "\n"

print(res)

with open("src\\Experimenter_Scripts\\Measurement6_Results.txt", "w") as file:
    file.write(res)

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
run_length = [2]
cause_size = [2]

res_BF = "But-For Causality:\n"
res_Act = "Actual Causality:\n"

# Dummy Computation to prevent starting issues:

experimenter = exp.Experimenter_Computation(2, 2, 2, 2)
experimenter.experiment_BF_Cause()
experimenter.experiment_Actual_Cause()

for t in ta_length:
    for r in run_length:
        if r > t:
            continue
        time = 0
        for c in cause_size:
            experimenter = exp.Experimenter_Computation(sample_size, t, r, c)
            time += experimenter.experiment_BF_Cause()

        res_BF += "t = " + str(t) + ", r = " + str(r) + " --> Time: " + str(time / len(cause_size)) + "\n"

for t in ta_length:
    for r in run_length:
        if r > t:
            continue
        time = 0
        for c in cause_size:
            experimenter = exp.Experimenter_Computation(sample_size, t, r, c)
            time += experimenter.experiment_Actual_Cause()

        res_Act += "t = " + str(t) + ", r = " + str(r) + " --> Time: " + str(time / len(cause_size)) + "\n"


res = "\nMeasurements Results: \n\n" + "Sample size:" + str(sample_size) + "\nCause sizes: " + str(cause_size) + "\n\n"
res += res_BF + "\n" + res_Act + "\n"

print(res)
with open("src\\Experimenter_Scripts\\Measurement9_Results.txt", "w") as file:
    file.write(res)

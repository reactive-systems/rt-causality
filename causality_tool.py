import sys, getopt, os
from src import cause_checker as cc
import pyuppaal as pyu

ERROR_MESSAGE = "causality_tool.py -d -c <causekind> -s <systemfile> -t <tracefile> -e <eventfile>' (for cause checking)\n"
ERROR_MESSAGE += "causality_tool.py -f -c <causekind> -s <systemfile> -t <tracefile> (for cause computation)\n"
ERROR_MESSAGE += "with <causekind>: \"b\" but-for causality,  \"m\" minimal but-for causality, \"a\" actual causality"

def set_verifyta_path_main():
    
    try:
        file = open(os.path.join(os.path.dirname(__file__), "verifyta_path.txt"), "r")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print("No \"verifyta_path.txt\"-file found in the directory")
        sys.exit(2)

    pyu.set_verifyta_path(data)



def main(argv):

    set_verifyta_path_main()
    
    computation = None      #True for cause computation, false for cause checking
    cause_str = None
    systemfile = None
    tracefile = None
    eventfile = None
    
    #Parsing command line parameter
    try:
        opts, args = getopt.getopt(argv,"hdfc:s:t:e:",["causenotion=", "sfile=", "tfile=", "efile="])
    except getopt.GetoptError:
        print (ERROR_MESSAGE)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print (ERROR_MESSAGE)
            sys.exit()
        elif opt == '-f':
            computation = True
        elif opt == '-d':
            computation = False 
        elif opt in ("-c", "--causenotion"):
            cause_str = arg
        elif opt in ("-s", "--sfile"):
            systemfile = arg    
        elif opt in ("-t", "--tfile"):
            tracefile = arg    
        elif opt in ("-e", "--efile"):
            eventfile = arg  
     
    if computation is None: 
        print("Invalid program arguments: Mode is not specified, give argument \"-d\" for checking a cause or argument \"-f\" for computing causes" )
        print (ERROR_MESSAGE)
        sys.exit(2)
    if cause_str is None:
        print("Invalid program arguments: Cause notion must be specified using argument \"-c\"")
        print (ERROR_MESSAGE)
        sys.exit(2)
    if systemfile is None:
        print("Invalid program arguments: System file missing")
        print (ERROR_MESSAGE)
        sys.exit(2)
    if tracefile is None:
        print("Invalid program arguments: Trace file missing")
        print (ERROR_MESSAGE)        
        sys.exit(2)

    #Processing command line parameter
    system_path = os.path.join(os.path.dirname(__file__), systemfile)
    trace_path = os.path.join(os.path.dirname(__file__), tracefile)

    if cause_str == 'b':
        cause = 0
    elif cause_str == 'm':
        cause = 1
    elif cause_str == 'a':
        cause = 2
    else: 
        print("Invalid program arguments: Cause notion is invalidly specified")
        print (ERROR_MESSAGE)        
        sys.exit(2)


    #Call respective functionalities
    if computation:
        CC = cc.get_cause_computer(system_path, trace_path)

        if cause == 0:
            print("Computation of but-for causes not available, we compute minimal but-for causes instead")
            res = CC.compute_But_For_Cause(True)
        elif cause == 1: 
            res = CC.compute_But_For_Cause(True)
        elif cause == 2:
            res = CC.compute_Actual_Cause(True)
    
    
    else:
        if eventfile is None:
            print("Invalid program arguments: set of event file missing")
            print (ERROR_MESSAGE)        
            sys.exit(2)
        
        event_path = os.path.join(os.path.dirname(__file__), eventfile)

        CC = cc.get_cause_checker(system_path, trace_path, event_path)
        if cause == 0:
            CC.check_But_For_Cause()
        elif cause == 1: 
            CC.check_Min_But_For_Cause()
        elif cause == 2:
            CC.check_Actual_Cause()

    sys.exit()

        
if __name__ == "__main__":
   main(sys.argv[1:])
# Real-Time-Causality-Tool
Project repository for a Python tool for checking and computing causes in concrete runs of real-time systems modeled in Uppaal. 

## Installaling

For executing the tool, you must have installed 
- a current Python version (3.10.0 or newer)
- Uppaal: https://uppaal.org/ (we run the tool with Uppaal version 4.1, but also other versions should be fine)
- the Python library pyuppaal: https://pypi.org/project/pyuppaal/1.0.0/

After downloading our project files, you have to set at first the verifyta-path (that is the system path for executing Uppaal's model checker) . 
Include the absolute path to verfifyta in the <em>verifyta_path.txt</em> file in the top folder of our project.

By default, this should be the following:

>Windows: absolute_path_to_uppaal\bin-Windows\verifyta.exe
>
>Linux  : absolute_path_to_uppaal/bin-Linux/verifyta
>
>macOS  : absolute_path_to_uppaal/bin-Darwin/verifyta

Now, you should be able to execute the Python files from this project. 

## Usage and Functionalities

For running the main functionalities of the tool, execute the Python file <em>causality_tool.py</em> together with the following program arguments:
>"-d" for checking a cause or "-f" for computing causes
>
>"-c <cause_kind>", whereby <cause_kind> can be instantiated with
>  
>   <cause_kind> = "b" for but-for causality, 
>
>    <cause_kind> = "m" for minimal but-for causality, or
>
>    <cause_kind> = "a" for actual causality
>
>"-s <systemfile>", with <systemfile> the xml-file of a Uppaal system containing the automaton and effect query
>
>"-t <tracefile>", with <tracefile> the txt-file containing considered trace 
>
>"-e <eventfile>", with <eventfile> the txt-file containing the considered set of events (only necessary to give as argument for the computation of causes)

For instance, the following commands performs minimal but-for cause testing for event set Example_3_1_1\Cause1:
> python .\causality_tool.py -d -c m -s .\Thesis_Examples\Example_3_1_1\TA.xml -t .\Thesis_Examples\Example_3_1_1\Trace.txt -e .\Thesis_Examples\Example_3_1_1\Cause1.txt

Converseley, the following command performs actual cause computations for system .\Thesis_Examples\Example_3_1_1\TA.xml and trace .\Thesis_Examples\Example_3_1_1\Trace.txt.
> python .\causality_tool.py -f -c a -s .\Thesis_Examples\Example_3_1_1\TA.xml -t .\Thesis_Examples\Example_3_1_1\Trace.txt 

The experiment scripts used for measurements and literature examples should be executable without any arguments. 

### Supported Uppaal Systems 

We support Uppaal systems only with one agent, enabling non-internal actions to be performed by dummy handshaking. The dummy handshaker might either be given directly as template already in the input file (the template must then have the name "Dummy_Handshaker") or is added by the tool itself. Besides this restriction, we do also not support parameters, shared global variables, further chaneltypes. Also, we only allow fixed clock assignments.

We refer also to the multiple examples for more details on the possible input forms for the Uppaal System.

### Representing Runs, Traces, and Sets of Events

We represent only the concrete actions and delays of a run (i.e., its trace). We can handle delay traces, delay lasso traces, and timestamp traces as well as the corresponding sets of events. See the traces and causes in <em>Example_3_1_5</em> and <em>Example_3_2_3</em> for more details on the input format. 


## About the Project
The tool was developed in the course of the master's project on "Counterfactual Causality in Real-Time Systems" by Felix Jahn, advised by Julian Siber, and supervised by Prof. Bernd Finkbeiner, Ph.D. at Saarland University. Causes are checked and computed relying on the formal notions of causality in real-time systems developed in this thesis. 

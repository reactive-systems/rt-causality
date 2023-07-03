#File containing an functionalities and classes for systematic runtime measurements

import trace_structs as ts
import ta_structs as ta
import cause_checker as cc
import os
import random
import time


#Constructs measured system for checking causes
def get_experiment_checking_system(ta_length: int) -> ta.System:

    locations = []
    transitions = []

    for i in range(ta_length):
        locations.append(ta.Location(None, i, ta.Position(i*300, 0), "x <= 2"))
        transitions.append(ta.Transition(None, i, i + 1, ta.Position(i*300 + 150, 0), "x <= 1", "a!", "x := 0"))
        transitions.append(ta.Transition(None, i, ta_length + 1, ta.Position(i*300 + 200, 100), "x > 1", "a!"))
        transitions.append(ta.Transition(None, i, ta_length + 1, ta.Position(i*300 + 200, 100), None, "b!"))

    locations.append(ta.Location(None, ta_length, ta.Position(ta_length*300, 0), None, "succ"))
    transitions.append(ta.Transition(None, ta_length, ta_length, ta.Position(ta_length*300+50, 0), None, "a!"))
    transitions.append(ta.Transition(None, ta_length, ta_length, ta.Position(ta_length*300+50, 0), None, "b!"))

    locations.append(ta.Location(None, ta_length + 1, ta.Position(ta_length*300, 500), None, "fail"))
    transitions.append(ta.Transition(None, ta_length + 1, ta_length + 1, ta.Position(ta_length*300 + 50, 500), None, "a!"))
    transitions.append(ta.Transition(None, ta_length + 1, ta_length + 1, ta.Position(ta_length*300 + 50, 500), None, "b!"))

    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata'))

    template = ta.Template(None, "Experiment", locations, 0, transitions, None, None)
    ta_path = os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata\\Experiment_TA.xml')

    return ta.System(None, ta_path, "Experiment_Proc = Experiment();\nsystem Experiment_Proc;", "clock x;\nchan a, b;", [template], ["A[] not Proc_Experiment.fail"])

#Constructs measured system for computing causes
def get_experiment_compute_system(ta_length: int, trace_length: int, cause: ts.DelayCause) -> ta.System:

    locations = []
    transitions : list[transitions] = []

    for i in range(trace_length):
        locations.append(ta.Location(None, i, ta.Position(i*300, 0), "x <= 2"))
        transitions.append(ta.Transition(None, i, i + 1, ta.Position(i*300 + 150, 0), None, "a!", "x := 0"))
        transitions.append(ta.Transition(None, i, i + 1, ta.Position(i*300 + 150, 0), None, "b!", "x := 0"))

    locations.append(ta.Location(None, trace_length, ta.Position(trace_length*300, 0), None, "fail"))
    transitions.append(ta.Transition(None, trace_length, trace_length, ta.Position(trace_length*300+50, 0), None, "a!"))
    transitions.append(ta.Transition(None, trace_length, trace_length, ta.Position(trace_length*300+50, 0), None, "b!"))

    for delay_event in cause.delay_events:
        transitions[(delay_event[1] - 1) * 2].guard = "x <= 1"
        transitions.append(ta.Transition(None, delay_event[1] - 1, trace_length + 1, ta.Position((delay_event[1] - 1)*300 + 200, 100), "x > 1", "a!"))

    for action_event in cause.action_events:
        transitions[(action_event[1] - 1) * 2 + 1] = ta.Transition(None, action_event[1] - 1, trace_length + 1, ta.Position((action_event[1] - 1)*300 + 200, 100), None, "b!")

    for i in range (trace_length + 1, ta_length + 1):
        locations.append(ta.Location(None, i, ta.Position((i - 1)*300, 500), "x <= 2"))
        transitions.append(ta.Transition(None, i, i + 1, ta.Position((i - 1)*300 + 150, 500), None, "a!", "x := 0"))
        transitions.append(ta.Transition(None, i, i + 1, ta.Position((i - 1)*300 + 150, 500), None, "b!", "x := 0"))

    locations.append(ta.Location(None, ta_length + 1, ta.Position(ta_length *300, 500), None, "succ"))
    transitions.append(ta.Transition(None, ta_length + 1, ta_length + 1, ta.Position(ta_length*300+50, 500), None, "a!"))
    transitions.append(ta.Transition(None, ta_length + 1, ta_length + 1, ta.Position(ta_length*300+50, 500), None, "b!"))

    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata'))

    template = ta.Template(None, "Experiment", locations, 0, transitions, None, None)
    ta_path = os.path.join(os.path.dirname(__file__), 'Experimenter_Scripts\\Experiment_Automata\\Experiment_TA.xml')

    return ta.System(None, ta_path, "Experiment_Proc = Experiment();\nsystem Experiment_Proc;", "clock x;\nchan a, b;", [template], ["A[] not Proc_Experiment.fail"])

#Constructs measured trace
def get_experiment_check_trace(trace_length: int, cause: ts.DelayCause) -> ts.DelayTrace:

    delays = [1] * trace_length
    actions = ["a!"] * trace_length

    for delay_event in cause.delay_events:
        delays[delay_event[1] - 1] = 2

    for action_event in cause.action_events:
        actions[action_event[1] - 1] = "b!"

    return ts.DelayTrace(delays, actions)


def get_experiment_comp_trace(trace_length: int) -> ts.DelayTrace:

    delays = [1] * trace_length
    actions = ["a!"] * trace_length

    return ts.DelayTrace(delays, actions)


def to_cause_check(trace_length: int, events: list[int]) -> ts.DelayCause:

    delay_events = []
    action_events = []

    for id in events:
        if id < trace_length:
            delay_events.append(ts.DelayEvent((2, id + 1)))
        else:
            action_events.append(ts.ActionEvent(("b!", id - trace_length + 1)))

    return ts.DelayCause(delay_events, action_events)


def to_cause_comp(trace_length: int, events: list[int]) -> list[ts.DelayCause]:

    causes = []

    for id in events:
        if id < trace_length:
            causes.append(ts.DelayCause([ts.DelayEvent((1, id + 1))], []))
        else:
            causes.append(ts.DelayCause([], [ts.ActionEvent(("a!", id - trace_length + 1))]))

    return causes


#Experimenter class for cause checking
class Experimenter_Checking:

    def __init__ (self, sample_size: int,  ta_length: int , trace_length: int, cause_size: int):

        assert ta_length >= trace_length, "Trace cannot be longer than the automaton!"
        assert trace_length > 0, "Invalid trace length!"
        assert cause_size <= 2 * trace_length, "Cause size cannot be more than twice as large as the length of the trace!"

        self.sample_size = sample_size
        self.ta_length = ta_length
        self.trace_length = trace_length
        self.cause_size = cause_size

        self.system = get_experiment_checking_system(self.ta_length)
        self.system.to_UModel().save()

        self.event_ids = []
        self.causes = []
        self.traces = []
        for i in range(self.sample_size):
            self.event_ids.append(random.sample(range(0,2 * trace_length), cause_size))
            self.causes.append(to_cause_check(trace_length, self.event_ids[i]))
            self.traces.append(get_experiment_check_trace(trace_length, self.causes[i]))


    def experiment_BF_Cause(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_But_For_Cause())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)


    def experiment_Min_BF_Cause(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_Min_But_For_Cause())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)


    def experiment_Actual_Cause(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_Actual_Cause())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)


    def experiment_SAT(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_SAT())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)


    def experiment_CF_BF(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_CF_But_For())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)


    def experiment_CF_Act(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_checker = cc.CauseChecker(self.system, self.traces[i], self.causes[i])
            res.append(cause_checker.check_CF_Actual())

        end = time.time()

        print(res)

        return ((end - start)/self.sample_size)




#Experimenter class for cause computation
class Experimenter_Computation:


    def __init__ (self, sample_size: int,  ta_length: int , trace_length: int, cause_number: int):

        assert ta_length >= trace_length, "Trace cannot be longer than the automaton!"
        assert trace_length > 0, "Invalid trace length!"
        assert cause_number <= 2 * trace_length, "Cause size cannot be more than twice as large as the length of the trace!"

        self.sample_size = sample_size
        self.ta_length = ta_length
        self.trace_length = trace_length
        self.cause_size = cause_number

        self.trace = get_experiment_comp_trace(self.trace_length)

        self.event_ids = []
        self.causes = []
        self.systems : list[ta.System] = []
        for i in range(self.sample_size):
            self.event_ids.append(random.sample(range(0,2 * trace_length), cause_number))
            self.causes.append(to_cause_comp(trace_length, self.event_ids[i]))
            self.systems.append(get_experiment_compute_system(self.ta_length, self.trace_length, to_cause_check(self.trace_length, self.event_ids[i])))

        self.systems[0].to_UModel().save()


    def experiment_BF_Cause(self) -> float:

        res = []
        start = time.time()

        for i in range(self.sample_size):
            cause_comp = cc.CauseComputer(self.systems[i], self.trace)
            res.append(cause_comp.compute_But_For_Cause())

        end = time.time()

        print(self.causes)
        print(res)

        return ((end - start)/self.sample_size)


    def experiment_Actual_Cause(self) -> float:

        res = []

        start = time.time()

        for i in range(self.sample_size):
            cause_comp = cc.CauseComputer(self.systems[i], self.trace)
            res.append(cause_comp.compute_Actual_Cause())

        end = time.time()

        print(self.causes)
        print(res)

        return ((end - start)/self.sample_size)

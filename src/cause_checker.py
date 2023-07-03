from __future__ import annotations
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

import pyuppaal as pyu
import trace_structs as ts
import ta_structs as ta

# File containing the major part of the cause checking and cause computation algorithms.

def to_cf_query(query: str):

    match query[0:3]:
        case "A[]":
            return "E[]" + query[3:]
        case "A<>":
            return "E<>" + query[3:]
        case "E[]":
            return "A[]" + query[3:]
        case "E<>":
            return "A<>" + query[3:]
        case _:
            raise Exception("Query contains syntax errors or is not suitable for cause checking!")

def get_cause_computer(system_path: str, trace_path: str) -> CauseComputer:
    timed_automaton = ta.System(pyu.UModel(system_path))
    trace = ts.parse_trace_from_file(trace_path)
    return CauseComputer(timed_automaton, trace)

def get_cause_checker(system_path: str, trace_path: str, event_path: str) -> CauseChecker:
    timed_automaton = ta.System(pyu.UModel(system_path))
    trace = ts.parse_trace_from_file(trace_path)
    events = ts.parse_cause_from_file(event_path)
    return CauseChecker(timed_automaton, trace, events, True)


# Class checking whether a given set of event is a but-for, minimal but-for or actual cause for a given effect in a trace of a timed automaton.

class CauseChecker:

    def __init__ (self, system: ta.System, trace: ts.DelayTrace | ts.DelayTraceLasso | ts.TimestampTrace, cause: ts.DelayCause | ts.TimestampCause, print_progress: bool = False):

        assert len(system.templates) == 1 or (len(system.templates) == 2 and system.templates[1].name == "Dummy_Handshaker"), "System seems to model a network (to many templates)"

        assert len(system.queries) == 1, "System that should be cause checked has more than one query."
        assert (isinstance(trace, (ts.DelayTrace, ts.DelayTraceLasso)) and isinstance(cause, ts.DelayCause)) or (isinstance(trace, ts.TimestampTrace) and isinstance(cause, ts.TimestampCause)), "Type of trace and cause do not match."

        self.system = system
        self.system.templates = [self.system.templates[0]] # delete dummy template
        self.trace = trace
        self.cause = cause
        self.query = self.system.queries[0]
        self.print_progress = print_progress


    def print_cause_checker(self):
        print ("- Real-time system path:", self.system.model_path)
        print ("- Trace:", self.trace)
        print ("- Effect formula:", self.system.queries[0])
        print ("- Set of events: ", self.cause)


    def check_SAT_Effect(self) -> bool:

        cf_trace_template = None

        if isinstance(self.trace, ts.TimestampTrace):
            trace = self.trace.to_delay()
        else:
            trace = self.trace

        cf_trace_template = trace.cf_automaton(ts.DelayCause([],[]), self.system.all_actions, False)

        if isinstance(trace, ts.DelayTrace):
            cf_trace_template.sat_check()

        cf_trace_system = ta.System(None, self.system.model_path[:len(self.system.model_path)-4] + "_CF.xml", None, None, [cf_trace_template])
        cf_system = self.system.intersect(cf_trace_system)

        cf_system.templates.append(self.system.dummy_handshaker)
        cf_system.queries = [to_cf_query(cf_system.queries[0])]
        cf_system.set_standard_system()

        if not cf_system.verify():
            if self.print_progress:
                print("SAT-condition satisfied")
            return True
        else:
            if self.print_progress:
                print("SAT-condition not satisfied, run does not satisfy the effect")
            return False


    def check_SAT(self) -> bool:
        if not self.trace.is_satisfied(self.cause):
            if self.print_progress:
                print("SAT-condition not satisfied, trace does not satisfy the cause")
            return False
        else:
            return self.check_SAT_Effect()


    def check_CF(self, actual: bool) -> bool:

        cf_trace_template = self.trace.cf_automaton(self.cause, self.system.all_actions)
        cf_trace_system = ta.System(None, self.system.model_path[:len(self.system.model_path)-4] + "_CF.xml", None, None, [cf_trace_template])

        cf_system = None
        if actual:
            cf_system = self.system.contingency_automaton([self.trace]).intersect(cf_trace_system)
        else:
            cf_system = self.system.intersect(cf_trace_system)

        cf_system.templates.append(self.system.dummy_handshaker)
        cf_system.queries = [to_cf_query(cf_system.queries[0])]
        cf_system.set_standard_system()

        if cf_system.verify():
            if self.print_progress:
                if actual:
                    print("CF-Actual-condition satisfied")
                else:
                    print("CF-But-For-condition satisfied")
            return True
        else:
            if self.print_progress:
                if actual:
                    print("CF-Actual-condition not satisfied")
                else:
                    print("CF-But-For-condition not satisfied")
            return False


    def check_CF_But_For(self) -> bool:
        return self.check_CF(False)


    def check_CF_Actual(self) -> bool:
        return self.check_CF(True)


    def check_MIN(self, actual) -> bool:

        for sub_cause in self.cause.get_subsets():
            sub_cause_checker = CauseChecker(self.system, self.trace, sub_cause)
            if actual:
                if sub_cause_checker.check_CF_Actual():
                    if self.print_progress:
                        print ("MIN-condition not satisfied: the following smaller cause satisfies SAT and CF-Actual as well:")
                        print (sub_cause)
                    return False
            else:
                if sub_cause_checker.check_CF_But_For():
                    if self.print_progress:
                        print ("MIN-condition not satisfied: the following smaller cause satisfies SAT and CF-But-For as well:")
                        print (sub_cause)
                    return False

        if self.print_progress:
            print("MIN-condition satisfied")
        return True


    def check_MIN_But_For(self) -> bool:
        return self.check_MIN(False)


    def check_MIN_Actual(self) -> bool:
        return self.check_MIN(True)


    def check_But_For_Cause(self) -> bool:

        print ("Checking but-for cause:")
        self.print_cause_checker()
        print ("\nStart cause checking...\n")

        res = self.check_SAT() and self.check_CF_But_For()

        print("\nCause checking was done for:")
        self.print_cause_checker()
        print("- Causality notion: But-For Causality")

        if res:
            print("\nResult: The set of events is a but-for cause!\n")
        else:
            print("\nResult: The set of events is NO but-for cause!\n")
        return res


    def check_Min_But_For_Cause(self) -> bool:
        print ("Checking minimal but-for cause:")
        self.print_cause_checker()
        print ("\nStart cause checking...\n")

        res = self.check_SAT() and self.check_CF_But_For() and self.check_MIN_But_For()

        print("\nCause checking was done for:")
        self.print_cause_checker()
        print("- Causality notion: Minimal But-For Causality")

        if res:
            print("\nResult: The set of events is a minimal but-for cause!\n")
        else:
            print("\nResult: The set of events is NO minimal but-for cause!\n")
        return res

    def check_Actual_Cause(self) -> bool:
        print ("Checking minimal but-for cause:")
        self.print_cause_checker()
        print ("\nStart cause checking...\n")

        res = self.check_SAT() and self.check_CF_Actual() and self.check_MIN_Actual()

        print("\nCause checking was done for:")
        self.print_cause_checker()
        print("- Causality notion: Minimal But-For Causality")

        if res:
            print("\nResult: The set of events is an actual cause!\n")
        else:
            print("\nResult: The set of events is NO actual but-for cause!\n")
        return res



# Class computing minimal but-for or actual causes for a given effect in a trace of a timed automaton.

class CauseComputer:

    def __init__ (self, system: ta.System, trace: ts.DelayTrace | ts.DelayTraceLasso | ts.TimestampTrace):
        assert len(system.queries) == 1, "System that should be cause checked has more than one query."

        self.system = system
        self.trace = trace


    def print_cause_computer(self):
        print ("- Real-time system path", self.system.model_path)
        print ("- Trace:", self.trace)
        print ("- Effect formula:", self.system.queries[0])


    def compute_Cause(self, actual: bool, print_progress: bool = True) -> list[ts.DelayCause] | list[ts.TimestampCause]:

        if actual:
            print ("Computaion of actual causes:")
        else:
            print ("Computation of minimal but-for cuases:")
        self.print_cause_computer()
        print ("\nStart cause computation...\n")

        if isinstance(self.trace, ts.TimestampTrace):
            cause_checker_sat = CauseChecker(self.system, self.trace, ts.TimestampCause([],[]))
        else:
            cause_checker_sat = CauseChecker(self.system, self.trace, ts.DelayCause([],[]))

        if not cause_checker_sat.check_SAT_Effect():
            print("Run does not satisfy the effect, hence there is no cause at all!")
            return []

        all_events = self.trace.get_all_events()

        res = []
        work = []

        if isinstance(self.trace, ts.TimestampTrace):
            work.append(ts.TimestampCause([], []))
        else:
            work.append(ts.DelayCause([], []))

        for event in all_events.delay_events | all_events.action_events:
            cur_res = []
            for cause in list(map(lambda c: c.add_event(event), work)):
                if any(res_cause.is_subcause(cause) for res_cause in cur_res):
                    continue
                if print_progress:
                    print("Checking: ", cause)
                cause_check = CauseChecker(self.system, self.trace, cause)
                if actual:
                    if cause_check.check_CF_Actual():
                        cur_res.append(cause)
                    else:
                        work.append(cause)
                else:
                    if cause_check.check_CF_But_For():
                        cur_res.append(cause)
                    else:
                        work.append(cause)
            res += cur_res

        print("\nCauses were computed for:")
        self.print_cause_computer()
        if actual:
            print("- Causality notion: Actual Causality")
        else:
            print("- Causality notion: Minimal But-For Causality")
        print("\nResults:", res, "\n")

        return res


    def compute_Actual_Cause(self, print_progress: bool = True) -> list[ts.DelayCause] | list[ts.TimestampCause]:
       return self.compute_Cause(True, print_progress)


    def compute_But_For_Cause(self, print_progress: bool = True) -> list[ts.DelayCause] | list[ts.TimestampCause]:
       return self.compute_Cause(False, print_progress)

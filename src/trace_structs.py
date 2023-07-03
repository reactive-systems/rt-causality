# File with datastructures for configurations, different kinds of traces and causes of timed automata.

from __future__ import annotations

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from typing import NewType
import ta_structs as ta 
import re

# Type definitions for Events 

DelayEvent = NewType("DelayEvent", tuple[int,int])
TimestampEvent = NewType("TimestampEvent", tuple[int,int])
ActionEvent = NewType("ActionEvent", tuple[str,int])


# Functions for the parsing of timed traces

def parse_trace_from_file (file_path: str) -> DelayTrace | DelayTraceLasso | TimestampTrace: 
    #open text file in read mode
    file = open(file_path, "r")
 
    #read whole file to a string
    data = file.read()
    
    #close file
    file.close()

    return parse_trace(data)


def parse_trace(input: str) -> DelayTrace | DelayTraceLasso | TimestampTrace:
    
    trace_str = re.sub('(?m)^ *//.*\n?', '', input).replace("\n", "")

    if "Delay trace:" in trace_str:
        res_tuple = parse_raw_trace(trace_str)
        return(DelayTrace(res_tuple[0], res_tuple[1]))
    
    if "Timestamp trace:" in trace_str:
        res_tuple = parse_raw_trace(trace_str)
        return(TimestampTrace(res_tuple[0], res_tuple[1]))
    
    if "Lasso delay trace:" in trace_str:
        prefix_str = trace_str[trace_str.find("Prefix part: "):trace_str.rfind("Lasso")]
        lasso_str = trace_str[trace_str.find("Lasso part: "):]
        prefix_tuple = parse_raw_trace(prefix_str)
        lasso_tuple = parse_raw_trace(lasso_str)
        return(DelayTraceLasso(prefix_tuple[0], prefix_tuple[1], lasso_tuple[0], lasso_tuple[1]))
    
    raise Exception("Syntax error in trace that was tried to be parsed!")     


def parse_raw_trace(input: str) -> tuple[list[int], list[str]]:
    times = []
    actions = []
    trace_list = list(map (lambda s: s.split(", "), re.findall('<(.*?)\>', input)))
    for item in trace_list:
        if not item[0].isnumeric():
            raise Exception("Invalid Trace is tried to be parsed: non integer delay")
        times.append(int(item[0])) #fehler behandlung
        action = item[1]
        if action == '-':
            continue
        elif action == 'tau':
            actions.append(None)
        else: 
            actions.append(action)
    return(times, actions)


def parse_cause_from_file (file_path: str) -> DelayCause | TimestampCause: 
    #open text file in read mode
    file = open(file_path, "r")
 
    #read whole file to a string
    data = file.read()
    
    #close file
    file.close()

    return parse_cause(data)


def parse_cause(input: str) -> DelayCause | TimestampCause:
    
    trace_str = re.sub('(?m)^ *//.*\n?', '', input).replace("\n", "")

    if "Delay cause:" in trace_str:
        res_tuple = parse_raw_cause(trace_str)
        return(DelayCause(res_tuple[0], res_tuple[1]))
    
    if "Timestamp cause:" in trace_str:
        res_tuple = parse_raw_cause(trace_str)
        return(TimestampCause(res_tuple[0], res_tuple[1]))

    raise Exception("Syntax error in cause that was tried to be parsed!")     

def parse_raw_cause(input: str) -> tuple[list[tuple[int, int]], list[ActionEvent]]:
    time_events = []
    action_events = []
    trace_list = list(map (lambda s: s.split(", "), re.findall('[(](.*?)[)]', input)))
    for item in trace_list: 
        if item[0].replace(".", "").isnumeric():
            time_events.append((int(item[0]), int(item[1])))
        else: 
            action_events.append((item[0], int(item[1])))
    return(time_events, action_events)



# Configuration class, implementing the necessary functionalities to reconstruct a run from its corresponding trace

class Configuration: 

    def __init__(self, location: int, clocks: list[str]):

        self.location = location

        self.clock_assignment: dict[str, int] = {}

        for clock in clocks:
            self.clock_assignment[clock] = 0


    def __repr__(self) -> str:

        return "Cofinguration:\nLocation: " + str(self.location) + "\nClock Assignment: " + self.clock_assignment.__str__()

    def update_clocks(self, expression: str | None) -> None:
        
        if expression is None:
            return

        assignments = expression.replace(' ', '').replace('\n', '').split(",") 
        for exp in assignments:
            exp_split = exp.split(':=')
            
            if len(exp_split) != 2:
                raise Exception("Invalid Expression in Update")
            
            if exp_split[0] in self.clock_assignment:
                self.clock_assignment[exp_split[0]] = int(exp_split[1])
            else: 
                raise Exception("Non existing clock is tried to be updated")

    def delay(self, delay: int) -> None:
        
        for key in self.clock_assignment:    
            self.clock_assignment[key] = self.clock_assignment[key] + delay

    def satisfies(self, guard: str | None) -> bool:

        if guard is None:
            return True

        simple_conditions = guard.replace(' ', '').split('&&')
        
        for cond in simple_conditions:
            if not self.satisfies_simple_condition(cond): 
                return False

        return True
    
    def satisfies_simple_condition(self, condition: str) -> bool:
        
        if '==' in condition:
            cond_split = condition.split('==')
            if cond_split[0] in self.clock_assignment:
                return self.clock_assignment[cond_split[0]] == int(cond_split[1])
            
        elif '<=' in condition:
            cond_split = condition.split('<=')
            if cond_split[0] in self.clock_assignment:
                return self.clock_assignment[cond_split[0]] <= int(cond_split[1])
            
        elif '>=' in condition:
            cond_split = condition.split('>=')
            if cond_split[0] in self.clock_assignment:
                return self.clock_assignment[cond_split[0]] >= int(cond_split[1])
        
        elif '<' in condition:
            cond_split = condition.split('<')
            if cond_split[0] in self.clock_assignment:
                return self.clock_assignment[cond_split[0]] < int(cond_split[1])
            
        elif '>' in condition:
            cond_split = condition.split('>')
            if cond_split[0] in self.clock_assignment:
                return self.clock_assignment[cond_split[0]] > int(cond_split[1])
  
    def setter_expression(self):
        if len(self.clock_assignment) == 0:
            return None
        
        res = ""
        for key in self.clock_assignment:
            res += ",\n" + key + " := " + str(self.clock_assignment[key]) 

        return res[2:]   


# Data structures representing the different kinds of traces. Classes also include functionality to construct counterfactual trace automata.       

class DelayTrace:
    
    def __init__(self, delays: list[int], actions: list[str]):
       
        self.number_delays = len(delays)
        self.number_actions = len(actions)

        assert self.number_delays == self.number_actions or self.number_delays == self.number_actions + 1, "Number of delays and actions does not match."
        
        self.delays = delays
        self.actions = actions


    def __repr__(self) -> str:
        
        res = "Delay trace: "
        
        for i in range(self.number_actions):
            res += "<" + str(self.delays[i]) + ", " + str(self.actions[i] or "tau") + "> "
        
        if self.number_actions + 1 == self.number_delays:
            res += "<" + str(self.delays[self.number_delays-1]) + ", ->"
        
        return res
    

    def to_timestamp(self) -> TimestampTrace:
        
        timestamps = []
        sum = 0
        
        for delay in self.delays:
            sum += delay
            timestamps.append(sum)

        return TimestampTrace(timestamps, self.actions)


    def extend_to_lasso(self, delays_lasso: list[int], actions_lasso: list[str]) -> DelayTraceLasso:
        return DelayTraceLasso(self.delays, self.actions, delays_lasso, actions_lasso)


    def is_satisfied(self, cause: DelayCause) -> bool:
        
        try:    
            for delay_event in cause.delay_events:
                if self.delays[delay_event[1]-1] != delay_event[0]:
                    return False
            for action_event in cause.action_events:
                if self.actions[action_event[1]-1] != action_event[0]:
                    return False
            return True

        except IndexError:
            return False
        

    def get_all_events(self) -> DelayCause: 
       
        delay_events = []
        action_events = []

        for i in range(self.number_delays):
            delay_events.append((self.delays[i], i+1))
    
        for i in range(self.number_actions):
            action_events.append((self.actions[i], i+1))

        return DelayCause(delay_events, action_events)  


    def cf_automaton(self, cause: DelayCause, all_actions: list[str], infinite_cf: bool = True, node_dist: int = 400) -> ta.Template:

        max_id = -1

        delay_indices = list(map(lambda p: p[1], cause.delay_events))
        action_indices = list(map(lambda p: p[1], cause.action_events))
        if self.number_delays == self.number_actions + 1:
            action_indices.append(self.number_delays)

        locations: list[ta.Location] = []
        for i in range(self.number_delays + 1):
            max_id = max_id + 1
            inv = None
            if (i+1) not in delay_indices:
                try: 
                    inv = f"d <= {self.delays[i]}"
                except IndexError:
                    inv = None
            locations.append(ta.Location(None, max_id, ta.Position(node_dist*max_id, 0), inv))

        transitions: list[ta.Transition] = []
        for i in range(self.number_delays):
            if (i+1) in delay_indices:
                guard = None
            else:
                guard = f"d == {self.delays[i]}" 
            
            if (i+1) in action_indices:
                y_pos = - 150 * len(all_actions) / 2 + 75 
                for action in all_actions:
                    transitions.append(ta.Transition(None, i, i+1, ta.Position(i*node_dist + node_dist//2 - 10, y_pos), guard, action, "d := 0", True)) 
                    y_pos += 150
            else: transitions.append(ta.Transition(None, i, i+1, ta.Position(i*node_dist + node_dist//2 - 10, 80), guard, self.actions[i], "d := 0"))  

        if infinite_cf:
            for action in all_actions:
                transitions.append(ta.Transition(None, max_id, max_id, ta.Position(max_id*400 + 90, 0), None, action)) 
        
        return ta.Template(None, "CF_Automaton", locations, 0, transitions, None, "clock d;")
        

class DelayTraceLasso:

    def __init__(self, delays_pre: list[int], actions_pre: list[str], delays_lasso: list[str], actions_lasso: list[str]):
        
        assert len(delays_pre) == len(actions_pre), "Number of delays and actions in the prefix-part are not equal."
        assert len(delays_lasso) == len(actions_lasso), "Number of delays and actions in the lasso-part are not equal."

        self.delays_pre = delays_pre
        self.actions_pre = actions_pre
        self.delays_lasso = delays_lasso
        self.actions_lasso = actions_lasso

        self.length_pre = len(self.delays_pre)
        self.length_lasso = len(self.delays_lasso) 


    def __repr__(self) -> str:
        
        res = "Lasso delay trace:\n"
        res += "Prefix part: "
        for i in range(self.length_pre):
            res += "<" + str(self.delays_pre[i]) + ", " + str(self.actions_pre[i] or "tau") + "> "
        
        res += "\nLasso part: "      
        for i in range(self.length_lasso):
            res += "<" + str(self.delays_lasso[i]) + ", " + str(self.actions_lasso[i] or "tau") + "> "

        return res


    def get_prefix_trace(self) -> DelayTrace:
        return DelayTrace(self.delays_pre, self.actions_pre)


    def is_satisfied(self, cause: DelayCause) -> bool:
        
        try:    
            for delay_event in cause.delay_events:
                if delay_event[1] <= self.length_pre:
                    if self.delays_pre[delay_event[1] - 1] != delay_event[0]:
                        return False
                else:
                     if self.delays_lasso[delay_event[1] - self.length_pre - 1] != delay_event[0]:
                        return False
            
            for action_event in cause.action_events:
                if action_event[1] <= self.length_pre:
                    if self.actions_pre[action_event[1] - 1] != action_event[0]:
                        return False
                else:
                     if self.actions_lasso[action_event[1] - self.length_pre - 1] != action_event[0]:
                        return False
                
            return True

        except IndexError:
            return False


    def get_all_events(self) -> DelayCause: 
       
        delay_events = []
        action_events = []

        for i in range(self.length_pre):
            delay_events.append((self.delays_pre[i], i+1))
            delay_events.append((self.actions_pre[i], i+1))

        for i in range(self.length_lasso):
            delay_events.append((self.delays_lasso[i], i + self.length_pre + 1)) 
            delay_events.append((self.actions_lasso[i], i + self.length_pre + 1)) 

        return DelayCause(delay_events, action_events)  
    

    def cf_automaton(self, cause: DelayCause, all_actions: list[str], node_dist: int = 400) -> ta.Template:

        max_id = -1

        delay_indices = list(map(lambda p: p[1], cause.delay_events))
        action_indices = list(map(lambda p: p[1], cause.action_events))

        locations: list[ta.Location] = []
        for i in range(self.length_pre + self.length_lasso):
            max_id = max_id + 1
            inv = None
            if (i+1) not in delay_indices:
                try: 
                    if i < self.length_pre:
                        inv = f"d <= {self.delays_pre[i]}"
                    else: 
                        inv = f"d <= {self.delays_lasso[i - self.length_pre]}"
                except IndexError:
                    inv = None
            locations.append(ta.Location(None, max_id, ta.Position(node_dist*max_id, 0), inv))

        transitions: list[ta.Transition] = []
        for i in range(self.length_pre + self.length_lasso):
            
            target_id = i+1
            if target_id == self.length_pre + self.length_lasso:
                target_id = self.length_pre 
            
            if (i+1) in delay_indices:
                guard = None
            else:
                if i < self.length_pre:
                    guard = f"d == {self.delays_pre[i]}"
                else:
                    guard = f"d == {self.delays_lasso[i - self.length_pre]}"      
            
            if (i+1) in action_indices:
                y_pos = - 150 * len(all_actions) / 2 + 75 
                for action in all_actions:
                    transitions.append(ta.Transition(None, i, target_id, ta.Position(i*node_dist + node_dist//2 - 10, y_pos), guard, action, "d := 0", True)) 
                    y_pos += 150
            else:
                action = None
                if i < self.length_pre:
                    action = self.actions_pre[i]
                else: 
                    action = self.actions_lasso[i - self.length_pre]
                transitions.append(ta.Transition(None, i, target_id, ta.Position(i*node_dist + node_dist//2 - 10, 80), guard, action, "d := 0"))  

        return ta.Template(None, "CF_Automaton", locations, 0, transitions, None, "clock d;")


    
class TimestampTrace:

    def __init__(self, timestamps: list[int], actions: list[str]):

        self.number_timestamps = len(timestamps)
        self.number_actions = len(actions)

        assert self.number_timestamps == self.number_actions or self.number_timestamps == self.number_actions + 1, "Number of timestamps and actions does not match."
        for i in range(self.number_timestamps - 1):
            assert timestamps[i] <= timestamps[i+1], "Timestamps are not monotonically increasing."
        
        self.actions = actions
        self.timestamps = timestamps


    def __repr__(self) -> str:
        res = "Timestamp trace: "
        for i in range(self.number_actions):
            res += "<" + str(self.timestamps[i]) + ", " + str(self.actions[i] or "tau") + "> "
        
        if self.number_actions + 1 == self.number_timestamps:
            res += "<" + str(self.timestamps[self.number_timestamps - 1]) + ", ->"
        
        return res


    def to_delay(self) -> DelayTrace:

        delays = []
        last_time = 0

        for time in self.timestamps:
            delays.append(time - last_time)
            last_time = time

        return DelayTrace(delays, self.actions)


    def is_satisfied(self, cause: TimestampCause) -> bool:
        
        try:    
            for time_event in cause.timestamp_events:
                if self.timestamps[time_event[1]-1] != time_event[0]:
                    return False
            for action_event in cause.action_events:
                if self.actions[action_event[1]-1] != action_event[0]:
                    return False
            return True

        except IndexError:
            return False


    def get_all_events(self) -> TimestampCause: 
       
        timestamp_events = []
        action_events = []

        for i in range(self.number_timestamps):
            timestamp_events.append((self.timestamps[i], i+1))
    
        for i in range(self.number_actions):
            action_events.append((self.actions[i], i+1))

        return DelayCause(timestamp_events, action_events)  
    

    #Remark for a possible extension to networks: for non networks, it would be sufficient to only use output actions here --> further arguemnt of cf_automaton

    def cf_automaton(self, cause: TimestampCause, all_actions: list[str], infinite_cf: bool = True, node_dist: int = 400) -> ta.Template:

        max_id = -1

        timestamp_indices = list(map(lambda p: p[1], cause.timestamp_events))
        action_indices = list(map(lambda p: p[1], cause.action_events))
        if self.number_timestamps == self.number_actions + 1:
            action_indices.append(self.number_timestamps)

        locations: list[ta.Location] = []
        for i in range(self.number_timestamps + 1):
            max_id = max_id + 1
            inv = None
            if (i+1) not in timestamp_indices:
                try: 
                    inv = f"t <= {self.timestamps[i]}"
                except IndexError:
                    inv = None

            locations.append(ta.Location(None, max_id, ta.Position(node_dist*max_id, 0), inv))

        transitions: list[ta.Transition] = []
        for i in range(self.number_timestamps):
            if (i+1) in timestamp_indices:
                guard = None
            else:
                guard = f"t == {self.timestamps[i]}" 
            
            if (i+1) in action_indices:
                y_pos = - 150 * len(all_actions) / 2 + 75 
                for action in all_actions:
                    transitions.append(ta.Transition(None, i, i+1, ta.Position(i*node_dist + node_dist//2 - 10, y_pos), guard, action, None, True)) 
                    y_pos += 150
            else: transitions.append(ta.Transition(None, i, i+1, ta.Position(i*node_dist + node_dist//2 - 10, 80), guard, self.actions[i], None))  

        if infinite_cf:
            for action in all_actions:
                transitions.append(ta.Transition(None, max_id, max_id, ta.Position(max_id*400 + 90, 0), None, action)) 
        
        return ta.Template(None, "CF_Automaton", locations, 0, transitions, None, "clock t;")


# Classes representing sets of events, once for the delay perspective, once for the timestamp perspective. 

class DelayCause: 

    def __init__(self, delay_events: set[DelayEvent], action_events: set[ActionEvent]):
        self.delay_events = set(delay_events)
        self.action_events = set(action_events)


    def __repr__(self) -> str:
        
        res = ""

        for delay in self.delay_events:
            res += delay.__str__() + ", "
        for action in self.action_events:
            res += "(" + str(action[0]) + ", " + str(action[1] or "tau") + ")" + ", "
        res = res[:len(res)-2]
        
        return "Delay cause: {" + res + "}"


    def get_subsets (self) -> list[DelayCause]:
        
        res = []

        for event in self.delay_events:
            cur_delay_events = self.delay_events.copy()
            cur_delay_events.remove(event)
            res.append(DelayCause(cur_delay_events, self.action_events))
            
        for event in self.action_events:
            cur_action_events = self.action_events.copy()
            cur_action_events.remove(event)
            res.append(DelayCause(self.delay_events, cur_action_events))

        return res    

    def add_event (self, event: DelayEvent | ActionEvent) -> DelayCause:
        if isinstance(event[0], int):
            return DelayCause(self.delay_events | {event}, self.action_events)
        elif isinstance (event[0], str):
            return DelayCause(self.delay_events, self.action_events | {event})
        else:
            raise Exception("Event that was tried to be added to the cause has wrong type!")
            
    def is_subcause (self, other: DelayCause) -> bool:
        for event in self.delay_events:
            if event not in other.delay_events:
                return False
        
        for event in self.action_events:
            if event not in other.action_events:
                return False 
            
        return True


class TimestampCause: 

    def __init__(self, timestamp_events: set[TimestampEvent], action_events: set[ActionEvent]):
        self.timestamp_events = set(timestamp_events)
        self.action_events = set(action_events)

    def __repr__(self) -> str:
        
        res = ""
        
        for time in self.timestamp_events:
            res += time.__str__() + ", "
        for action in self.action_events:
            res += "(" + str(action[0]) + ", " + str(action[1] or "tau") + ")" + ", "
        res = res[:len(res)-2]
        
        return "Timestamp cause: {" + res + "}"
    
    def get_subsets (self) -> list[TimestampCause]:
        
        res = []

        for event in self.timestamp_events:
            cur_timestamp_events = self.timestamp_events.copy()
            cur_timestamp_events.remove(event)
            res.append(TimestampCause(cur_timestamp_events, self.action_events))
            
        for event in self.action_events:
            cur_action_events = self.action_events.copy()
            cur_action_events.remove(event)
            res.append(TimestampCause(self.timestamp_events, cur_action_events))

        return res  

    def add_event (self, event: TimestampEvent | ActionEvent) -> TimestampCause:
        if isinstance(event[0], int):
            return TimestampCause(self.timestamp_events | {event}, self.action_events)
        elif isinstance (event[0], str):
            return TimestampCause(self.timestamp_events, self.action_events | {event})
        else:
            raise Exception("Event that was tried to be added to the cause has wrong type!")
            
    def is_subcause (self, other: TimestampCause) -> bool:
        for event in self.timestamp_events:
            if event not in other.timestamp_events:
                return False
        
        for event in self.action_events:
            if event not in other.action_events:
                return False 
            
        return True
# Datastructures representing Timed Automata: Locations, Transitions, Templates, Systems
# Those datastructures contain also the functionalities for intersecting automata
# The template and system datastructure contains as well methods for constructing the contingency automaton

from __future__ import annotations

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

import trace_structs as ts
import pyuppaal as pyu
import xml.etree.ElementTree as ET
from pyuppaal.iTools import UFactory as ufac
import itertools
import re

# Functions used for the intersection of automata

def cantor_pair(k1: int, k2:int) -> int:
    return (k1 + k2)*(k1 + k2 + 1) // 2 + k2

def str_connect(s1: None | str, s2: None | str, connector: str) -> None | str:
    if s1 == None or s1 == "":
        return s2
    elif s2 == None or s2 == "":
        return s1
    else:
        return s1 + connector + s2   
    

# Parsing and preprocessing functions
    
def get_declaration_info(declaration: str | None, keyword: str) -> list[str]: #can only handle chandeclaration in one line
    if declaration is None: 
        return []
    res = (list (map (lambda s: s.split(", "), re.findall(keyword + ' (.*?)\;', declaration))))
    return [item for sublist in res for item in sublist]
    
def get_clocks (declaration: str | None) -> list[str]:
    return get_declaration_info(declaration, 'clock')

def get_alphabet (declaration: str | None) -> list[str]:
    return get_declaration_info(declaration, 'chan')

def get_output_actions(alphabet: list [str]):
    return list(map (lambda s: s + "!", alphabet))

def get_input_actions(alphabet: list [str]):
    return list(map (lambda s: s + "?", alphabet))

def add_spaces(queries: list[str], templates: list[Template]) -> list[str]:
    
    query_dict: dict[str, str] = {}

    for template in templates:
        temp_name = template.name        
        for loc in template.locations:
            if loc.name is not None:
                new_loc_name = loc.name + " "
                query_dict[loc.name] = new_loc_name

    inter_queries = []

    for query in queries:
        for key in query_dict: 
            query = query.replace(key, query_dict[key])  
        inter_queries.append(query)
    
    return inter_queries


# Dummy handshaker for allowing action transitions in a single template

def dummy_handshaker(alphabet: list [str]) -> Template:
    dummy_loc = Location(None, 0, Position(0, 0))
    transitions = list(map (lambda action: Transition(None, 0, 0, Position(50, 0), None, action), get_input_actions(alphabet)))
    return Template(None, "Dummy_Handshaker", [dummy_loc], 0, transitions)



class Position: 

    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y 

    def __repr__(self):
        return f"Pos: ({self.x}, {self.y})"

    def add(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)
    
    def cart_middle(self, other: Position) -> Position:
        return Position((self.x + other.x) / 2, (self.y + other.y) / 2)


class Location:
    
    def __init__ (self, elem: ET.Element | None, id: int = None, pos: Position = None, inv: str = None, name: str = None, commited: bool = False):
            
        if elem is not None:
            assert elem.tag == "location", "The element used to create a location is no location but " + elem.tag

            self.id = int(elem.get("id")[2:])
            self.position = Position(int(elem.get("x")),int(elem.get("y")))
            
            name_elem = elem.find("name")
            if name_elem is None: 
                self.name = None
            else:
                self.name = name_elem.text

            inv_elem = elem.find("label")
            if inv_elem is None: 
                self.inv = None
            else:
                self.inv = inv_elem.text

            self.commited = elem.find("commited") != None
        
        else: 
            self.id = id
            self.position = pos
            self.inv = inv
            self.name = name
            self.commited = commited 

    def __repr__(self):
        return f"Location(id: {self.id}, pos: {self.position}, name: {self. name}, inv: {self.inv}, commited: {self.commited})"

    def to_ET(self):
        return ufac.location(self.id, self.position.x, self.position.y, self.inv, self.name, self.commited)

    def intersect(self, other: Location) -> Location:

        inter_id = cantor_pair(self.id, other.id)
        
        inter_position = self.position.add(other.position)

        inter_inv = str_connect(self.inv, other.inv, " && ")

        if self.name is None: 
            inter_name = None
        else:
            inter_name = self.name + "_" + str(other.id)

        return Location(None, inter_id, inter_position, inter_inv, inter_name, False) 


class Transition: 

    def __init__(self, elem: ET.Element | None, source: int = None, target: int = None, pos: Position = None, 
                        guard: str = None, sync: str = None, assignment: str = None, nail: bool = False):
        
        if elem is not None:
            assert elem.tag == "transition", "The element used to create a transition is no transtition but " + elem.tag

            source_elem = elem.find("source")
            assert source_elem != None, "There is no source for the transition that should be created."
            self.source = int(source_elem.get("ref")[2:])

            target_elem = elem.find("target")
            assert target_elem != None, "There is no target for the transition that should be created."
            self.target = int(target_elem.get("ref")[2:])

            label_elem = elem.find("label")
            if label_elem == None:
                self.position = None 
            else: 
                self.position = Position(int(label_elem.get("x")),int(label_elem.get("y")))

            self.guard = None
            self.sync = None
            self.assignment = None
            
            for label in elem.findall("label"):
                kind = label.get("kind")
                if kind == "guard":
                    self.guard = label.text
                elif kind == "synchronisation":
                    self.sync = label.text
                elif kind == "assignment":
                    self.assignment = label.text
                else:
                    raise Exception("There was an unknown label when creating a transition")

            self.nail = elem.find("nail") != None
        
        else:
            self.source = source
            self.target = target
            self.position = pos
            self.guard = guard
            self.sync = sync
            self.assignment = assignment
            self.nail = nail 

    def __repr__(self):
        return f"Transition(source: {self.source}, target: {self.target}, pos: {self.position}, guard: {self.guard}, sync: {self.sync}, assignment: {self.assignment}, nail: {self.nail})"

    def to_ET(self):
        if self.position is not None:
            return ufac.transition(self.source, self.target, self.position.x, self.position.y, self.guard, self.sync, self.assignment, self.nail)
        else:
            return ufac.transition(self.source, self.target, None, None, self.guard, self.sync, self.assignment, self.nail)
  
    def intersect(self, other: Transition) -> None | Transition:
        if self.sync != other.sync:
            return None

        inter_source = cantor_pair(self.source, other.source)
        inter_target = cantor_pair(self.target, other.target)

        if self.position != None and other.position != None: 
            inter_position = self.position.add(other.position)
        elif self.position != None:
            inter_position = self.position
        else:
            inter_position = other.position       #For prettier output: compute the middle of the transition target and source

        inter_guard = str_connect(self.guard, other.guard, " && ")

        inter_assignment = str_connect(self.assignment, other.assignment, ",\n")

        return Transition(None, inter_source, inter_target, inter_position, inter_guard, self.sync, inter_assignment, self.nail) 


class Template: 

    def __init__(self, elem: ET.Element | None, name: str = None, locations : list[Location] = [], init: int = None, transitions: list[Transition] = [],
                        parameter: str = None, declaration: str = None):
        
        if elem is not None:
            assert elem.tag == "template", "The element used to create a template is no template but " + elem.tag

            self.name = elem.find("name").text

            self.locations = [Location(loc) for loc in elem.findall("location")]

            self.init = int(elem.find("init").get("ref")[2:])

            self.transitions = [Transition(trans) for trans in (elem.findall("transition"))]

            self.parameter = None       #Tool does not support parameters 

            declaration_elem = elem.find("declaration")
            if declaration_elem == None:
                self.declaration = None 
            else: 
                self.declaration = declaration_elem.text

        else:
            self.name = name
            self.locations = locations
            self.init = init
            self.transitions = transitions
            self.parameter = parameter
            self.declaration = declaration


    def __repr__(self):
        return f"Template: \n name: {self.name}, init: {self.init}\n locations: {self.locations} \n transitions: {self.transitions}\n declaration: {self.declaration})"

    def get_location_ids(self) -> list[int]:
        location_ids = []
        for loc in self.locations:
            location_ids.append(loc.id)
        return location_ids

    def to_ET(self):
        return ufac.template(self.name, [loc.to_ET() for loc in self.locations], self.init, [trans.to_ET() for trans in self.transitions], self.parameter, self.declaration)

    # Function intersecting two templates
    def intersect(self, other: Template) -> Template:
        inter_locs = list(map (lambda l: l[0].intersect(l[1]), itertools.product(self.locations, other.locations)))
        
        inter_trans: list[Transition] = []
        trans_prod = itertools.product(self.transitions, other.transitions)
        for (trans1, trans2) in trans_prod:
            trans_cand = trans1.intersect(trans2)
            if trans_cand is not None:
                inter_trans.append(trans_cand)


        inter_name = self.name + "_INTER" 

        inter_init = cantor_pair(self.init, other.init)

        inter_declaration = str_connect(self.declaration, other.declaration, "\n")

        return Template(None, inter_name, inter_locs, inter_init, inter_trans, None, inter_declaration)
    
    def execute_transition(self, configuration: ts.Configuration, action: str): 
        
        for transition in self.transitions:
            if transition.source == configuration.location and transition.sync == action and configuration.satisfies(transition.guard):
                configuration.location = transition.target
                configuration.update_clocks(transition.assignment)
                return

        raise Exception("Found no executable transition for this configuration")
    

    def contingency_automaton_lasso(self, trace: ts.DelayTraceLasso, clocks: list[str], actions: list[str], node_dist: int = 300) -> Template:
        
        name_con = self.name + "_CON"

        # construct product locations
        locations_con = []
        for i in range(trace.length_pre + trace.length_lasso):
            for loc in self.locations:
                new_pos = loc.position.add(Position(0, node_dist * i))
                if loc.name is None: 
                    new_name = None
                else:
                    new_name = loc.name + "_" + str(i)
                locations_con.append(Location(None, cantor_pair(loc.id, i), new_pos, loc.inv, new_name, loc.commited))
        
        init_con = cantor_pair(self.init, 0)

        transitions_con = []
        for transition in self.transitions:

            # add normal transitions
            for i in range(trace.length_pre + trace.length_lasso):
                new_source = cantor_pair(transition.source, i)
                new_target = cantor_pair(transition.target, i + 1)

                if i + 1 == trace.length_pre + trace.length_lasso:
                    new_target = cantor_pair(transition.target, trace.length_pre)

                try:
                    new_pos = transition.position.add(Position(0, node_dist * i)) 
                except AttributeError:
                    new_pos = None
                new_trans = Transition(None, new_source, new_target, new_pos, transition.guard, transition.sync, transition.assignment, transition.nail)
                transitions_con.append(new_trans) 


        # add contingency transitions
        configuration = ts.Configuration(self.init, clocks)  
        for i in range(trace.length_pre + trace.length_lasso):
            
            if i < trace.length_pre:
                delay = trace.delays_pre[i]
                action = trace.actions_pre[i]
            else: 
                delay = trace.delays_lasso[i - trace.length_pre]
                action = trace.actions_lasso[i - trace.length_pre]

            configuration.delay(delay)
            self.execute_transition(configuration, action)

            new_target = cantor_pair(configuration.location, i + 1)
            if i + 1 == trace.length_pre + trace.length_lasso:
                new_target = cantor_pair(configuration.location, trace.length_pre)       

            for loc in self.locations:
                new_source = cantor_pair(loc.id, i)
                new_pos = loc.position.add(Position(0, node_dist * i + node_dist / 2))

                for action in actions + [None]:
                    new_trans = Transition(None, new_source, new_target, new_pos, None, action, configuration.setter_expression())
                    transitions_con.append(new_trans)    


        return Template(None, name_con, locations_con, init_con, transitions_con, self.parameter, self.declaration)


    def contingency_automaton(self, given_trace: ts.DelayTrace | ts.DelayTraceLasso | ts.TimestampTrace, clocks: list[str], actions: list[str], node_dist: int = 300) -> Template:

        if isinstance(given_trace, ts.DelayTraceLasso):
            return self.contingency_automaton_lasso(given_trace, clocks, actions, node_dist)

        trace: ts.DelayTrace = None
        if isinstance(given_trace, (ts.TimestampTrace)):
            trace = given_trace.to_delay()
        else:
            trace = given_trace


        name_con = self.name + "_CON"

        # construct product locations
        locations_con = []
        for i in range(len(trace.delays) + 1):
            for loc in self.locations:
                new_pos = loc.position.add(Position(0, node_dist * i))
                if loc.name is None: 
                    new_name = None
                else:
                    new_name = loc.name + "_" + str(i)
                locations_con.append(Location(None, cantor_pair(loc.id, i), new_pos, loc.inv, new_name, loc.commited))

        init_con = cantor_pair(self.init, 0)

        transitions_con = []
        for transition in self.transitions:

            # add transitions in all but the last copies:
            for i in range(len(trace.delays) + 1):
                new_source = cantor_pair(transition.source, i)
                new_target = cantor_pair(transition.target, i + 1)
                if i  == len(trace.delays):
                    new_target = cantor_pair(transition.target, len(trace.delays))

                try:
                    new_pos = transition.position.add(Position(0, node_dist * i)) 
                except AttributeError:
                    new_pos = None
                new_trans = Transition(None, new_source, new_target, new_pos, transition.guard, transition.sync, transition.assignment, transition.nail)
                transitions_con.append(new_trans) 
                
        configuration = ts.Configuration(self.init, clocks)  
        for i in range(len(trace.delays)):
            configuration.delay(trace.delays[i])
            self.execute_transition(configuration, trace.actions[i])

            new_target = cantor_pair(configuration.location, i + 1)

            for loc in self.locations:
                new_source = cantor_pair(loc.id, i)
                new_pos = loc.position.add(Position(0, node_dist * i + node_dist / 2))

                for action in actions + [None]:
                    new_trans = Transition(None, new_source, new_target, new_pos, None, action, configuration.setter_expression())
                    transitions_con.append(new_trans)    


        return Template(None, name_con, locations_con, init_con, transitions_con, self.parameter, self.declaration)
    

    def sat_check(self) -> None:
        self.locations[len(self.locations)-1].inv = "d <= 0"



class System: 

    def __init__ (self, umodel: pyu.UModel | None, model_path: str = None, system: str = None, declaration: str = None, templates: list[Template] = [], queries: list[str] = [], add_query_spaces: bool = True):
        
        if umodel is not None:
            self.model_path = umodel.model_path
            self.system = umodel.system
            self.declaration = umodel.declaration
            self.templates = [Template(temp) for temp in umodel.element_tree.findall("template")]
            if add_query_spaces: 
                self.queries = add_spaces(umodel.queries, self.templates)
            else:
                self.queries = umodel.queries
        else: 
            self.model_path = model_path 
            self.system = system
            self.declaration = declaration
            self.templates = templates
            if add_query_spaces: 
                self.queries = add_spaces(queries, self.templates)
            else:
                self.queries = queries

        self.alphabet = get_alphabet(self.declaration) 
        self.all_actions = [None] + get_input_actions(self.alphabet) + get_output_actions(self.alphabet)
        self.dummy_handshaker = dummy_handshaker(self.alphabet)

        self.clocks = get_clocks(self.declaration)


    def set_standard_system(self):

        res = "//System Declarations:\n\n"
        for temp in self.templates:
            res += "Proc_" + temp.name + " = " + temp.name + "();\n"

        res += "\nsystem "

        for temp in self.templates:
            res += "Proc_" + temp.name + ", "

        res = res[:len(res)-2] + ";"

        self.system = res


    def to_UModel(self):
        
        root = ET.Element("nta")
        
        if self.declaration is not None: 
            dec_elem = ET.Element("declaration")
            dec_elem.text = self.declaration
            root.append(dec_elem)
        
        for template in self.templates:
            root.append(template.to_ET())
        
        if self.system is not None: 
            sys_elem = ET.Element("system")
            sys_elem.text = self.system
            root.append(sys_elem)

        elem_tree = ET.ElementTree(root)

        with open(self.model_path, 'w', encoding='utf-8') as f:
            elem_tree.write(
                self.model_path, encoding="utf-8", xml_declaration=True)

        umodel = pyu.UModel(self.model_path)

        umodel.set_queries(self.queries)
        return umodel
    
    def verify(self, trace_path: str = None, verify_options: str = None) -> bool:
        verify_str = self.to_UModel().verify(trace_path, verify_options)
        # print(verify_str)  # Uncomment for printing the model checking result 
        if "Formula is satisfied" in verify_str:
            return True
        elif "Formula is NOT satisfied" in verify_str:
            return False
        else:
            raise Exception("System verification failed, no result was returned")
              

    def intersect(self, other: System) -> System:

        assert len(self.templates) == len(other.templates), "Systems that are tried to intersect do not have the same number of templates." 

        inter_model_path = self.model_path[:len(self.model_path)-4] + "_INTER.xml" 
        inter_declaration = str_connect(self.declaration, other.declaration, "\n")
        inter_templates = list(map(lambda t1, t2: t1.intersect(t2), self.templates, other.templates))
        inter_queries = self.intersection_queries(other)
        
            
        inter_sys = System(None, inter_model_path, None, inter_declaration, inter_templates, inter_queries, False)
        inter_sys.set_standard_system()

        return inter_sys


    def intersection_queries(self, other: System) -> list[str]:
        
        id_lists = []
        new_template_names = []
        for i in range(len(self.templates)):
            id_lists.append(other.templates[i].get_location_ids())
            new_template_names.append(self.templates[i].name + "_INTER")

        return self.query_product(id_lists, new_template_names)


    def query_product(self, id_lists: list[list[int]], new_template_names: list[str]) -> list[str]:

        query_dict: dict[str, str] = {}

        for i in range(len(self.templates)):
            temp_name = self.templates[i].name
            
            for loc in self.templates[i].locations:
                if loc.name is not None:
                    new_loc_name = "("
                    for other_id in id_lists[i]:
                        new_loc_name += "Proc_" + new_template_names[i] + "." + loc.name + "_" + str(other_id) + " or "
                    new_loc_name = new_loc_name[:len(new_loc_name)-4] + " )"
                    
                    query_dict["Proc_" + temp_name + "." + loc.name + " "] = new_loc_name + " "

        inter_queries = []

        for query in self.queries:
            for key in query_dict: 
                query = query.replace(key, query_dict[key])  
            inter_queries.append(query)
        
        return inter_queries
        
    
    def contingency_automaton(self, traces: list[ts.DelayTrace] | list[ts.DelayTraceLasso] | list[ts.TimestampTrace]) -> System:
        templates_con = []
        for i in range(len(traces)):
            templates_con.append(self.templates[i].contingency_automaton(traces[i], self.clocks, self.all_actions))

        model_path_con = self.model_path[:len(self.model_path)-4] + "_CON.xml" 
        queries_con = self.contingency_queries(traces)

            
        sys_con = System(None, model_path_con, None, self.declaration, templates_con, queries_con, False)
        sys_con.set_standard_system()

        return sys_con
    
    def contingency_queries(self, traces: list[ts.DelayTrace] | list[ts.DelayTraceLasso] | list[ts.TimestampTrace]) -> list[str]: 

        id_lists = []
        new_template_names = []
        for i in range(len(traces)):
            trace_length: int
            if isinstance(traces[i], ts.DelayTrace):
                trace_length = traces[i].number_delays
            elif isinstance(traces[i], ts.DelayTraceLasso):
                trace_length = traces[i].length_pre + traces[i].length_lasso - 1
            else:
                trace_length = traces[i].number_timestamps
            id_lists.append(list(range(0, trace_length + 1)))
            new_template_names.append(self.templates[i].name + "_CON")


        return self.query_product(id_lists, new_template_names)

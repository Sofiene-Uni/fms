from graphviz import Digraph
from IPython.display import Image, display

class Graph():
    
    def __init__(self, sim):
        self.sim = sim
        
    def plot_net(self, fired_transitions:list=[] , external_mask:list=[]):
        dot = Digraph(comment='Petri Net')
        dot.attr(label=f'Environment: {self.sim.label}\nTime Step: {self.sim.clock}', fontsize='20', splines='true' ,labelloc='t'  )
        
        # Add places
        places_by_role = {}
        for place in self.sim.places.values():
            
            token_color=""
            if place.token_container:
                for token in place.token_container:
                    token_color=token_color+str(token.color)
                    
            ntokens=str(len(place.token_container))

            if place.show:
                if place.enabled :  
                    if place.type  in ["p"]:
                        dot.node(place.uid, shape='circle', label=ntokens, style='filled', fillcolor='white', fontsize='16', width='0.75',penwidth='1')
                        
                    elif place.type in ["b" ,"s"]:
                        dot.node(place.uid, shape='circle', label= ntokens, style='filled', fillcolor='white', fontsize='16', width='0.75',penwidth='1')
                    elif place.type in ["d"]:
                         dot.node(place.uid, shape='circle', label=ntokens, style='filled', fillcolor='white', fontsize='16', width='1',penwidth='2')
                    elif place.type in ["f"]:
                        dot.node(place.uid, shape='circle', label=ntokens, style='filled,dotted', fillcolor='white', fontsize='16')
                else :
                    
                    dot.node(place.uid, shape='circle', label=ntokens, style='filled', fillcolor='red', fontsize='16', width='0.75',penwidth='1')
                    
                if place.role not in places_by_role:
                    places_by_role[place.role] = []
                    
                places_by_role[place.role].append(place.uid)

        # Add transitions
        transitions_by_role = {}
        for transition in self.sim.transitions.values():
            if transition.show:
            
                
                if  transition.type == "t" :
                    dot.node(transition.uid, shape='box', label="", style='filled,rounded', fillcolor='lightblue', fontsize='10', height='0.2')
                elif transition.type == "a" :
                    dot.node(transition.uid, shape='box', label=str(transition.color), style='filled,rounded', fillcolor='lightgrey', fontsize='10', height='0.2')
                elif transition.type == "c" :
                    fillcolor = 'white' if transition.check_state() else 'black'
                    dot.node(transition.uid, shape='box', label="", style='filled,rounded', fillcolor=fillcolor, fontsize='10', height='0.2')
                    

                if transition.uid in fired_transitions:
                      dot.node(transition.uid, shape='box', label="", style='filled,rounded', fillcolor='greenyellow', fontsize='10', height='0.2')
                      
                if transition.role not in transitions_by_role:
                    transitions_by_role[transition.role] = []
                transitions_by_role[transition.role].append(transition.uid)

        # Add arcs
        for place in self.sim.places.values():
            if place.show:
                for child in place.children:
                    if child.show:
                        dot.edge(place.uid, child.uid)

        for transition in self.sim.transitions.values():
            if transition.show:
                for child in transition.children:
                    if child.show:
                        dot.edge(transition.uid, child.uid)

        # Merge specific keys in places_by_role for symmetry
        def merge_keys(data, keys_to_merge, new_key):
            merged_values = []
            for key in keys_to_merge:
                if key in data:
                    merged_values.extend(data[key])
                    del data[key]
            data[new_key] = merged_values
            return data



        places_by_role = merge_keys(places_by_role, ['job', 'job_idle'], 'job')
        places_by_role = merge_keys(places_by_role, ['agv_transporting', 'agv_ready'], 'avg')
        places_by_role = merge_keys(places_by_role, ['machine_processing', 'machine_idle'], 'machine')
        places_by_role = merge_keys(places_by_role, ["tool_request", "tool_idle"], 'tool')
        places_by_role = merge_keys(places_by_role, ["tool_transporting","tool_transport_idle"], 'tool_transport')
        

        # Align places horizontally by role
        for role, place_uids in places_by_role.items():
            with dot.subgraph() as s:
                s.attr(rank='same')
                for uid in place_uids:
                    s.node(uid)

        # Align transitions horizontally by role
        for role, transition_uids in transitions_by_role.items():
            with dot.subgraph() as s:
                s.attr(rank='same')
                for uid in transition_uids:
                    s.node(uid)

        # Render the graph
        dot_data = dot.pipe(format='png')
        display(Image(dot_data))
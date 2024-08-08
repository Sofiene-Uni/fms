import copy 
from ptrl.common.instance_loader import InstanceLoader
from ptrl.common.build_blocks import Token, Place, Transition

class Petri_build:
    """
    A class representing a Petri net for Job Shop Scheduling Problems (JSSP).

    Attributes:
        instance_id (str): The ID of the JSSP instance.
        instance (pd.DataFrame): The JSSP instance data.
        n_jobs (int): The number of jobs in the instance.
        n_machines (int): The number of machines in the instance.
        max_bound (int): The maximum number of operations or tokens.

        places (dict): A dictionary containing Place objects.
        transitions (dict): A dictionary containing Transition objects.
    """

    def __init__(self, instance_id,
                 
                 layout=1,
                 benchmark='Raj',
                 n_agv=1,
                 n_tt=0,
                 dynamic=False,
                 size=(100, 20),
                 ):
        """
        Initialize the Petri net with a JSSP instance.

        Parameters:
            instance_id (str): The ID of the JSSP instance.
            dynamic (bool): If True, the Petri net is dynamic.
            size (tuple): Size parameters for dynamic mode (default: (100, 20)).
            n_agv (int): Number of AGVs (default: 0).
            n_tt (int): Number of tool transports (default: 0).
            benchmark (str): Benchmark type for instance loading (default: 'Raj').
        """
        
        self.instance_id = instance_id
        self.instance=InstanceLoader(benchmark=benchmark,instance_id=instance_id,layout=layout) 
        self.n_jobs, self.n_machines, self.n_tools, self.max_bound = self.instance.specs
        self.layout = layout
        self.n_agv = n_agv
        self.n_tt = n_tt

        self.places = {}
        self.transitions = {}
        
        self.dynamic = dynamic
        
        if self.dynamic:
            self.n_jobs, self.n_machines = size
        
        self.LU = True  # 
        self.create_petri(LU=self.LU, show_flags=True)

    def __str__(self):
        """
        Get a string representation of the Petri net.

        Returns:
            str: A string representing the Petri net.
        """
        return f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines"

    def filter_nodes(self, node_role):
        """
        Filters nodes based on node role.

        Parameters:
            node_role (str): Role of nodes to filter.

        Returns:
            list: Filtered nodes.
        """
        filtered_nodes = []
        for place in self.places.values():
            if place.role == node_role:
                filtered_nodes.append(place.uid)

        for transition in self.transitions.values():
            if transition.role == node_role:
                filtered_nodes.append(transition.uid)
        return filtered_nodes

    def node_info(self, node_uid, display=False):
        """
        Retrieves information about a node based on its UID.

        Parameters:
            node_uid (str): UID of the node.
            display (bool): If True, print node information (default: False).

        Returns:
            object: The node object corresponding to the UID.
        """
        for node in list(self.places.values()) + list(self.transitions.values()):
            if node.uid == node_uid:
                if display:
                    print(node)
                return node

        print("Node not found!")

    def add_nodes_layer(self, genre="place", type_="", role="", colored=True, timed=False, show=True, number=1):
        """
        Add a layer of nodes (places or transitions) to the Petri net.

        Parameters:
            genre (str): Type of nodes ("place" or "trans").
            type_ (str): Type of the node.
            role (str): Role of the node.
            colored (bool): If True, nodes are colored.
            timed (bool): If True, nodes are timed.
            show (bool): If True, show nodes (default: True).
            number (int): Number of nodes to add.
        """
        if genre == "place":
            for i in range(number):
                color = i if colored else None
                place_name = f"{role} {i}"
                place = Place(label=place_name, type_=type_, role=role, color=color, timed=timed, show=show)
                self.places[place.uid] = place
        else:
            for i in range(number):
                color = i if colored else None
                transition_name = f"{role} {i}"
                transition = Transition(label=transition_name, type_=type_, role=role, color=color, timed=timed, show=show)
                self.transitions[transition.uid] = transition

    def add_connection(self, parent_role, child_role, contype="p2t", fc=False):
        """
        Add connections (arcs) between nodes in the Petri net.

        Parameters:
            parent_role (str): Role of parent nodes.
            child_role (str): Role of child nodes.
            contype (str): Connection type ("p2t" for place to transition, "t2p" for transition to place).
            fc (bool): True for a fully connected graph, False for pairwise connections.
        """
        if contype == "p2t":
            parent_nodes = [p for p in self.places.values() if p.role == parent_role]
            child_nodes = [t for t in self.transitions.values() if t.role == child_role]
        elif contype == "t2p":
            parent_nodes = [t for t in self.transitions.values() if t.role == parent_role]
            child_nodes = [p for p in self.places.values() if p.role == child_role]

        if fc:
            for parent in parent_nodes:
                for child in child_nodes:
                    parent.add_arc(child, parent=False)
                    child.add_arc(parent, parent=True)
        else:
            for parent, child in zip(parent_nodes, child_nodes):
                parent.add_arc(child, parent=False)
                child.add_arc(parent, parent=True)

    def add_tokens(self):
        """
        Add tokens (representing job operations) to the Petri net.
        """
       
        for place in self.places.values():
            if place.type == "f":  # Add token for job operations
                place.token_container.append(Token())
                
                
        for job, uid in enumerate(self.filter_nodes("job")):
            try:
                for i, (machine,tool, process_time) in enumerate(self.instance.job_sequences[job]):
            
                    self.places[uid].token_container.append(
                        Token(initial_place=uid, color=(job, machine,tool, None),
                              time_features=[process_time,None,None, 0, 0] ,    # the rest is added later
                              rank=i))
                            
                    
                if self.LU:  # Add unload token
                    self.places[uid].token_container.append(
                        Token(initial_place=uid, color=(job, None ,None, None ),
                              time_features=[0,None,0, 0, 0],
                              rank=i + 1,
                              role="u"))
                
            except:
                pass
                #for dynamic token adding behaviour 
                        
        
          
    def create_petri(self, LU, show_flags):
        """
        Create the Petri net structure with predefined nodes and connections.

        Parameters:
            LU (bool): If True, include load and unload operations.
            show_flags (bool): If True, show flags in node creation.
        """
        
        nodes_layers = [
            ("place", "f", "job_idle",  True, False, show_flags, self.n_jobs),
            ("place", "b", "job", True, False, True, self.n_jobs),
            ("trans", "c", "job_select",  False, False, True, self.n_jobs),
            ("place", "s", "machine_sorting",  False, False, True, 1),
            ("trans", "a", "machine_sort",  True, False, True, self.n_machines),
            ("place", "b", "machine_buffer",  True, False, True, self.n_machines),
            ("trans", "c", "machine_allocate",  False, False, True, self.n_machines),
            ("place", "p", "machine_processing",  True, True, True, self.n_machines),
            ("place", "f", "machine_idle",  True, False, show_flags, self.n_machines),
            ("trans", "a", "machine_finish",  True, True, True, self.n_machines),
            ("place", "d", "delivery",  True, False, True, self.n_machines),
        ]

        layers_to_connect = [
            ("job_idle", "job_select", "p2t", False),
            ("job", "job_select", "p2t", False),
            ("machine_sorting", "machine_sort", "p2t", True),
            ("machine_sort", "machine_buffer", "t2p", False),
            ( "machine_buffer" ,"machine_allocate","p2t", False),
            ("machine_idle", "machine_allocate", "p2t", False),
            ("machine_allocate", "machine_processing", "t2p", False),
            ("machine_processing", "machine_finish", "p2t", False),
            ("machine_finish", "machine_idle", "t2p", False),
            ("machine_finish", "delivery", "t2p", False),
            ("machine_finish", "job_sorting", "t2p", True),
        ]
        
        if self.n_agv > 0 :
            nodes_layers += [
                ("place", 'f', "next_job_prep", True, False, show_flags, self.n_jobs),
                ("place", "b", "agv_buffer",  False, False, True, 1),
                ("trans", "c", "agv_select",  False, False, True, self.n_agv),
                ("place", "p", "agv_dead_heading", True, True, True, self.n_agv),
                ("trans", "a", "agv_wait", True, False, True, self.n_agv),
                ("place", "b", "agv_waiting", True, False, True, self.n_agv),
                ("trans", "a", "agv_start", False, False, True, self.n_agv),
                ("place", "p", "agv_transporting", True, True, True, self.n_agv),
                ("place", "f", "agv_idle",  True, False, show_flags, self.n_agv),
                ("trans", "a", "agv_finish",  False, True, True, self.n_agv),
                ("place", "s", "next_job_sorting", False, False, True, 1),
                ("trans", "a", "next_job_sort", True, False, True, self.n_jobs),
                ("place", "s", "agv_request_sorting", False, False, False, 1),
                ("trans", "a", "agv_request_sort", True, False, True, self.n_agv),
                ("place", "f", "next_job_ready", True, False, show_flags, self.n_agv),
                ("place", "s", "job_sorting",  False, False, False, 1),  
                ("trans", "a", "job_sort",  True, False, show_flags, self.n_agv),
                ]
            layers_to_connect += [
                ("next_job_prep", "job_select", "p2t", False),
                ("job_select", "agv_buffer", "t2p", True),
                ("agv_buffer", "agv_select", "p2t", True),
                ("agv_idle", "agv_select", "p2t", False),
                ("agv_select", "agv_dead_heading", "t2p", False),
                ("agv_dead_heading", "agv_wait", "p2t", False),
                ("agv_wait", "agv_waiting", "t2p", False),
                ("agv_waiting", "agv_start", "p2t", False),
                ("agv_start", "agv_transporting", "t2p", False),
                ("agv_transporting", "agv_finish", "p2t", False),
                ("agv_finish", "agv_idle", "t2p", False),
                ("agv_finish", "next_job_sorting", "t2p", True),
                ("next_job_sorting", "next_job_sort", "p2t", True),
                ("next_job_sort", "next_job_prep", "t2p", False),
                ("agv_finish", "machine_sorting", "t2p", True),
                ("agv_finish", "agv_request_sorting", "t2p", True),
                ("agv_request_sorting", "agv_request_sort", "p2t", True),
                ("agv_request_sort", "next_job_ready", "t2p", False),
                ("next_job_ready", "agv_start", "p2t", False),
                # ("job_sorting", "job_sort", "p2t", True),
                # ("job_sort", "agv_start", "t2p", False),
                ]
            layers_to_connect.remove(("job_idle", "job_select", "p2t", False))
        else :
            layers_to_connect += [("job_select", "machine_sorting", "t2p", True)]
                
        if self.n_tt > 0 :
            nodes_layers += [
                
                ("place", "s", "request_sorting",  False, False, True, 1),
                ("trans", "a", "request_sort",  True, False, True, self.n_tools),
                ("place", "b", "tool_request",  True, False, True, self.n_tools),
                ("place", "f", "tool_idle",  True, False, show_flags, self.n_tools),
                ("trans", "c", "tool_select",  False, False, True, self.n_tools),
                ("place", "f", "tool_transport_idle",  False, False, show_flags, self.n_tt),
                ("place", "b", "tool_request_buffer",  True, False, True, 1),
                ("trans", "c", "tool_transport_select",  False, False, True, self.n_tt),
                ("place", "b", "tool_transport_buffer",  True, False, True, self.n_tt),
                ("place", "p", "tool_transport_dead_heading",  True, True, True, self.n_tt),
                ("trans", "a", "tool_transport_start",  True, False, True, self.n_tt),
                ("place", "p", "tool_transporting",  True, True, True, self.n_tt),
                ("trans", "a", "transport_finish",  False, True, True, self.n_tt),
                ("place", "s", "machine_sorting_T",  False, False, True, 1),
                ("trans", "a", "machine_sort_T",  True, False, True, self.n_machines),
                ("place", "b", "machine_buffer_T",  True, False, True, self.n_machines),
                ("place", "s", "tools_sorting",  False, False, False, 1),  
                ("trans", "a", "tool_sort",  True, False, show_flags, self.n_tools)
                ]
            
            layers_to_connect += [ 
               
                ("job_select", "request_sorting", "t2p", True),
                ("request_sorting", "request_sort", "p2t", True),
                ("request_sort", "tool_request", "t2p", False),
                ("tool_request", "tool_select", "p2t", False),
                ("tool_idle", "tool_select", "p2t", False),
                ("tool_select", "tool_request_buffer","t2p", True),
                ("tool_request_buffer","tool_transport_select","p2t", True),
                ("tool_transport_select",  "tool_transport_dead_heading", "t2p", False),
                ("tool_transport_dead_heading", "tool_transport_start", "p2t", False),
                ("tool_transport_start", "tool_transporting", "t2p", False),
                ("transport_finish", "tool_transport_idle", "t2p", False),
                ("tool_transport_idle", "tool_transport_select", "p2t", False),
                ("tool_transporting", "transport_finish", "p2t", False),
                ("transport_finish", "machine_sorting_T", "t2p", True),
                ("machine_sorting_T", "machine_sort_T", "p2t", True),
                ("machine_sort_T", "machine_buffer_T", "t2p", False),
                ("machine_buffer_T", "machine_allocate", "p2t", False),
                ("machine_finish", "tools_sorting", "t2p", True),
                ("tools_sorting", "tool_sort", "p2t", True),
                ("tool_sort", "tool_idle", "t2p", False), 
                ]

        if LU:
            nodes_layers += [("place", "d", "store", False, False, True, 1), ("trans", "a", "lu", False, False, True, 1)]
            layers_to_connect += [("machine_sorting", "lu", "p2t", False), ("lu", "store", "t2p", False)]

        for genre,type_, role, colored, timed, show, number in nodes_layers:
            self.add_nodes_layer(genre=genre, type_=type_, role=role, colored=colored, timed=timed, show=show, number=number)

        for parent_role, child_role, contype, full_connect in layers_to_connect:
            self.add_connection(parent_role, child_role, contype, full_connect)

        self.add_tokens()

        print(f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines X  {self.n_tools} Tools, AGVs: {self.n_agv}, TT: {self.n_tt}, Dynamic Mode: {self.dynamic}")

   
# %% Test
if __name__ == "__main__":
    
    benchmark='Raj'
    instance_id="ra01"
    layout =1
    n_agv= 2
    n_tt= 1
    
    petri=Petri_build(instance_id,layout, benchmark=benchmark ,n_agv=n_agv , n_tt=n_tt) 

    
    




    
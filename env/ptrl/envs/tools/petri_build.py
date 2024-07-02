import copy 
from ptrl.common.instance_loader import load_instance ,load_trans
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
                 dynamic=False,
                 size=(100, 20),
                 n_agv=0,
                 n_tt=0,
                 benchmark='Raj'):
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
        self.dynamic = dynamic
        self.instance_id = instance_id
        self.instance, specs = load_instance(self.instance_id, benchmark=benchmark)
        
        self.n_jobs, self.n_machines,self.n_tools, self.max_bound = specs
        self.n_agv = n_agv
        self.n_tt = n_tt

        self.places = {}
        self.transitions = {}
        
        if self.dynamic:
            self.n_jobs, self.n_machines = size
        
        self.tran_durations = load_trans(self.n_machines, benchmark=benchmark)
        
        
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

    def add_nodes_layer(self, genre="place", type_="", role="",rank=0, colored=True, timed=False, show=True, number=1):
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
                place = Place(label=place_name, type_=type_, role=role,rank=rank, color=color, timed=timed, show=show)
                self.places[place.uid] = place
        else:
            for i in range(number):
                color = i if colored else None
                transition_name = f"{role} {i}"
                transition = Transition(label=transition_name, type_=type_, role=role,rank=rank, color=color, timed=timed, show=show)
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
        def calc_time(origin, destination):
            try:
                trans_time = 0
                if origin is None:  # Load operation
                    trans_time = int(self.tran_durations.iloc[0][destination + 1])
                elif destination is None:  # Unload operation
                    trans_time = int(self.tran_durations.iloc[origin + 1][0])
                elif origin != destination:  # Change of machine operation
                    trans_time = int(self.tran_durations.iloc[origin + 1][destination + 1])
                return trans_time
            except:
                return 0

        for place in self.places.values():
            if place.type == "f":  # Add token for job operations
                place.token_container.append(Token())
                
                

        for job, uid in enumerate(self.filter_nodes("job")):
            current_machine = None
            try:
                for i, (machine,tool, time) in enumerate(self.instance[job]):
                    self.places[uid].token_container.append(
                        Token(initial_place=uid, color=(job, machine,tool),
                              process_time=time,
                              rank=i,
                              trans_time=calc_time(current_machine, machine),
                              ))

                    current_machine = copy.copy(machine)

                if self.LU:  # Add unload token
                    self.places[uid].token_container.append(
                        Token(initial_place=uid, color=(job, None ,None ),
                              process_time=time,
                              rank=i + 1,
                              trans_time=calc_time(current_machine, None),
                              role="u"))
            except:
                pass

    def create_petri(self, LU, show_flags):
        """
        Create the Petri net structure with predefined nodes and connections.

        Parameters:
            LU (bool): If True, include load and unload operations.
            show_flags (bool): If True, show flags in node creation.
        """

            
   
        nodes_layers = [
                ("place", "f", "job_idle", 0, True, False, show_flags, self.n_jobs),
                ("place", "b", "job", 1, True, False, True, self.n_jobs),
                ("trans", "c", "job_select", 0, False, False, True, self.n_jobs),
                ("place", "b", "selected_jobs", 1, False, False, True, 1),
                ("trans", "c", "agv_select", 0, False, False, True, self.n_agv),
                ("place", "p", "agv_transporting", 1, True, True, True, self.n_agv),
                ("place", "f", "agv_idle", 0, True, False, show_flags, self.n_agv),
                ("trans", "a", "agv_finish", 0, False, True, True, self.n_agv),
                ("place", "s", "machine_sorting", 1, False, False, True, 1),
                ("trans", "a", "machine_sort", 0, True, False, True, self.n_machines),
                ("place", "b", "machine_buffer", 1, True, False, True, self.n_machines),
                ("trans", "c", "machine_allocate", 0, False, False, True, self.n_machines),
                ("place", "p", "machine_processing", 1, True, True, True, self.n_machines),
                ("place", "f", "machine_idle", 0, True, False, show_flags, self.n_machines),
                ("trans", "a", "machine_finish", 0, True, True, True, self.n_machines),
                ("place", "d", "delivery", 0, True, False, True, self.n_machines),
                ("place", "s", "job_sorting", 1, False, False, False, 1),  
                
                ("trans", "a", "job_sort", 0, True, False, show_flags, self.n_jobs),
                ("place", "s", "request_sorting", 0, False, False, True, 1),
                ("trans", "a", "request_sort", 0, True, False, True, self.n_tools),
                ("place", "b", "tool_request", 1, True, False, True, self.n_tools),
                ("place", "f", "tool_idle", 0, True, False, show_flags, self.n_tools),
                ("trans", "c", "tool_select", 0, False, False, True, self.n_tools),
                ("place", "f", "tool_transport_idle", 0, False, False, show_flags, self.n_tt),
                ("place", "b", "tool_transport_buffer", 0, True, False, True, self.n_tt),
                ("trans", "c", "tool_transport", 0, False, False, True, self.n_tt),
                ("place", "p", "tool_transporting", 1, True, True, True, self.n_tt),
                ("trans", "a", "transport_finish", 0, False, True, True, self.n_tt),
                ("place", "s", "machine_sorting_T", 1, False, False, True, 1),
                ("trans", "a", "machine_sort_T", 0, True, False, True, self.n_machines),
                ("place", "b", "machine_buffer_T", 0, True, False, True, self.n_machines),
                ("place", "s", "tools_sorting", 1, False, False, False, 1),  
                ("trans", "a", "tool_sort", 0, True, False, show_flags, self.n_tools)
            ]
        

        layers_to_connect = [
            ("job_idle", "job_select", "p2t", False),
            ("job", "job_select", "p2t", False),
            ("job_select", "selected_jobs", "t2p", True),
            ("selected_jobs", "agv_select", "p2t", True),
            ("agv_idle", "agv_select", "p2t", False),
            ("agv_select", "agv_transporting", "t2p", False),
            ("agv_transporting", "agv_finish", "p2t", False),
            ("agv_finish", "agv_idle", "t2p", False),
            ("agv_finish", "machine_sorting", "t2p", True),
            ("machine_sorting", "machine_sort", "p2t", True),
            ("machine_sort", "machine_buffer", "t2p", False),
            ( "machine_buffer" ,"machine_allocate","p2t", False),
            ("machine_idle", "machine_allocate", "p2t", False),
            ("machine_allocate", "machine_processing", "t2p", False),
            ("machine_processing", "machine_finish", "p2t", False),
            ("machine_finish", "machine_idle", "t2p", False),
            ("machine_finish", "delivery", "t2p", False),
            ("machine_finish", "job_sorting", "t2p", True),
            ("job_sorting", "job_sort", "p2t", True),
            ("job_sort", "job_idle", "t2p", False),

            ("job_select", "request_sorting", "t2p", True),
            ("request_sorting", "request_sort", "p2t", True),
            ("request_sort", "tool_request", "t2p", False),
            ("tool_request", "tool_select", "p2t", False),
            ("tool_idle", "tool_select", "p2t", False),
            ("tool_select", "tool_transport_buffer", "t2p", True),
            ("tool_transport_buffer", "tool_transport", "p2t", True),
            ("tool_transport", "tool_transporting", "t2p", True),
            ("transport_finish", "tool_transport_idle", "t2p", False),
            ("tool_transport_idle", "tool_transport", "p2t", False),
            ("tool_transporting", "transport_finish", "p2t", False),
            ("transport_finish", "machine_sorting_T", "t2p", False),
            ("machine_sorting_T", "machine_sort_T", "p2t", True),
            ("machine_sort_T", "machine_buffer_T", "t2p", False),
            ("machine_buffer_T", "machine_allocate", "p2t", False),
            ("machine_finish", "tools_sorting", "t2p", True),
            ("tools_sorting", "tool_sort", "p2t", True),
            ("tool_sort", "tool_idle", "t2p", False),
        ]

        if LU:
            nodes_layers += [("place", "d", "store",0, False, False, True, 1), ("trans", "a", "lu",0, False, False, True, 1)]
            layers_to_connect += [("machine_sorting", "lu", "p2t", False), ("lu", "store", "t2p", False)]

        # Add nodes (places and transitions)
        for genre,type_, role,rank, colored, timed, show, number in nodes_layers:
            self.add_nodes_layer(genre=genre, type_=type_, role=role,rank=rank, colored=colored, timed=timed, show=show, number=number)

        # Add arcs (places and transitions)
        for parent_role, child_role, contype, full_connect in layers_to_connect:
            self.add_connection(parent_role, child_role, contype, full_connect)

        # Add job tokens
        self.add_tokens()

        print(f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines X  {self.n_tools} Tools, AGVs: {self.n_agv}, TT: {self.n_tt}, dynamic Mode: {self.dynamic}")

   
# %% Test
if __name__ == "__main__":
    
    benchmark='Raj'
    instance_id="ra01"
    n_agv= 2
    n_tt= 1
    
    petri=Petri_build(instance_id, benchmark=benchmark ,n_agv=n_agv , n_tt=n_tt) 
    

    
    




    
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
                 size=(100,20),
                 n_agv=0,
                 benchmark='Taillard'):
        """
        Initialize the Petri net with a JSSP instance.
        Parameters:
            instance_id (str): The ID of the JSSP instance.
        """
        self.dynamic=dynamic
        self.instance_id = instance_id
        self.instance, specs = load_instance(self.instance_id,benchmark=benchmark)    
        self.n_jobs, self.n_machines, self.max_bound = specs
        self.n_agv=n_agv
        
        
        self.places = {}
        self.transitions = {}
        
        if self.n_agv > 0 :  
            self.tran_durations = load_trans(self.n_machines,benchmark=benchmark)
            self.create_petri_agv()
        else :
            self.create_petri()

        if  self.dynamic : 
            self.n_jobs,self.n_machines=size
    
        #self.plot_net()


    def __str__(self):
        """
        Get a string representation of the Petri net.
        Returns:
            str: A string representing the Petri net.
        """
        return f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines"

    def add_nodes_layer(self, is_place=True, node_type="", number=1 ,color=None):
        """
        Add a layer of nodes (places or transitions) to the Petri net.

        Parameters:
            is_place (bool): True if nodes are places, False if transitions.
            node_type (str): The type of nodes to be added.
            number (int): The number of nodes to be added.
        """
        if is_place:
            for i in range(number): 
                if color==None:
                    place_name = f"{node_type} {i}"
                    place = Place(place_name, node_type, color=i)
                    self.places[place.uid] = place   
                    
                else :    #User defined color 
                    place_name = f"{node_type} {color}"
                    place = Place(place_name, node_type, color=color)
                    self.places[place.uid] = place
        else:
            for i in range(number):
                
                if color==None:
                    transition_name = f"{node_type} {i}"
                    transition = Transition(transition_name, node_type, color=i)
                    self.transitions[transition.uid] = transition
                    
                else : #User defined color 
                    
                    transition_name = f"{node_type} {color}"
                    transition = Transition(transition_name, node_type, color=color)
                    self.transitions[transition.uid] = transition
                    
                    

    def add_connection(self, parent_type, child_type, contype="p2t", full_connect=False):
        """
        Add connections (arcs) between nodes in the Petri net.

        Parameters:
            parent_type (str): The type of parent nodes.
            child_type (str): The type of child nodes.
            contype (str): Connection type ("p2t" for place to transition, "t2p" for transition to place).
            full_connect (bool): True for a fully connected graph, False for pairwise connections.
        """
        if contype == "p2t":
            parent_nodes = [p for p in self.places.values() if p.type == parent_type]
            child_nodes = [t for t in self.transitions.values() if t.type == child_type]
        elif contype == "t2p":
            parent_nodes = [t for t in self.transitions.values() if t.type == parent_type]
            child_nodes = [p for p in self.places.values() if p.type == child_type]

        if full_connect:
            for parent in parent_nodes:
                for child in child_nodes:
                    parent.add_arc(child, parent=False)
                    child.add_arc(parent, parent=True)
        else:
            for parent, child in zip(parent_nodes, child_nodes):
                parent.add_arc(child, parent=False)
                child.add_arc(parent, parent=True)
                

    def add_tokens(self,LU=False):
        """
        Add tokens to the Petri net.
        Tokens represent job operations .
        """
        

        def cal_time(origin,destination):
            try : 
                
                trans_time =0
                if origin == None: #load
                    trans_time=int (self.tran_durations.iloc[0][destination+1])
                elif destination == self.n_machines: #Unload
                     trans_time=int (self.tran_durations.iloc[origin+1][0])
                elif origin is not destination : # change of machine
                    trans_time=int (self.tran_durations.iloc[origin+1][destination+1])
                return trans_time
            
            except : 
                return 0
                
            
            
        for job, uid in enumerate(self.filter_nodes("job")):  
            current_machine=None  
            try : # only add token to the operation in the instance  (for dynamic variant ) 
                # operations tokens
                           
                for i,(machine,time) in enumerate (self.instance[job]) :
                    
                    self.places[uid].token_container.append( Token(initial_place=uid, color=(job, machine),
                                                                               process_time=time ,
                                                                               order=i ,
                                                                               trans_time= cal_time(current_machine,machine)))  

                    current_machine = copy.copy(machine)
       
                if  LU : #add the unload token   
                    self.places[uid].token_container.append( Token(initial_place=uid, color=(job, self.n_machines),
                                                                   process_time=time,
                                                                   order=i+1 ,
                                                                   trans_time= cal_time(current_machine,self.n_machines),
                                                                   type_="u"))         
            except : 
                pass # the reserve jobs are empty 


    def filter_nodes(self, node_type):
        """
        Filters nodes based on node type.
        Parameters:
            node_type (str): Type of nodes to filter.

        Returns:
            list: Filtered nodes.
        """
        filtered_nodes = []
        for place in self.places.values():
            if place.type == node_type:
                filtered_nodes.append(place.uid)

        for transition in self.transitions.values():
            if transition.type == node_type:
                filtered_nodes.append(transition.uid)

        return filtered_nodes
    
    
    
    def create_petri_agv(self,LU=True):

        nodes_layers = [
            (True, "job", self.n_jobs),
            (False, "select", self.n_jobs),
            (True , "agv",self.n_agv) , 
            (False , "transport",self.n_machines) ,   
            (True, "ready", self.n_machines),
            (False, "allocate", self.n_machines),
            (True, "machine", self.n_machines),
            (False, "finish_op", self.n_machines),
            (True, "finished_ops", self.n_machines),
        ]

        layers_to_connect = [
            ("job", "select", "p2t", False),
            ("select", "agv", "t2p", True),
            ("agv", "transport", "p2t", True),
            ("transport","ready","t2p", False),
            ("ready", "allocate", "p2t", False),
            ("allocate", "machine", "t2p", False),
            ("machine", "finish_op", "p2t", False),
            ("finish_op", "finished_ops", "t2p", False),
        ]
        
        
        # Add nodes: places and transitions
        for is_place, node_type, number in nodes_layers:
            self.add_nodes_layer(is_place, node_type, number)

        # Add arcs places and transitions
        for parent_type, child_type, contype, full_connect in layers_to_connect:
            self.add_connection(parent_type, child_type, contype, full_connect)
            

        if LU:
            self.add_nodes_layer(is_place=True, node_type="store", number=1 ,color=self.n_machines)
            self.add_nodes_layer(is_place=False, node_type="lu", number=1,color=self.n_machines)
            self.add_connection("agv", "lu", "p2t", full_connect=True)
            self.add_connection("lu", "store", "t2p", full_connect=False)
            
            
        # Add jobs tokens
        self.add_tokens(LU)
        
        
        print (f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines, AGVs:{self.n_agv} , dynamic Mode: {self.dynamic}")
        
        

    def create_petri(self):
        """Create the Petri net structure, adding nodes, connections, and tokens."""
        
        nodes_layers = [
            (True, "job", self.n_jobs),
            (False, "select", self.n_jobs),
            (True, "ready", self.n_jobs),
            (False, "allocate", self.n_machines),
            (True, "machine", self.n_machines),
            (False, "finish_op", self.n_machines),
            (True, "finished_ops", self.n_machines),
        ]

        layers_to_connect = [
            ("job", "select", "p2t", False),
            ("select", "ready", "t2p", False),
            ("ready", "allocate", "p2t", True),
            ("allocate", "machine", "t2p", False),
            ("machine", "finish_op", "p2t", False),
            ("finish_op", "finished_ops", "t2p", False),
           ]
        

        # Add nodes: places and transitions
        for is_place, node_type, number in nodes_layers:
            self.add_nodes_layer(is_place, node_type, number)

        # Add arcs places and transitions
        for parent_type, child_type, contype, full_connect in layers_to_connect:
            self.add_connection(parent_type, child_type, contype, full_connect)
             
        # Add jobs tokens
        self.add_tokens()

        print (f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines, AGVs:{self.n_agv} , dynamic Mode: {self.dynamic}")
        
        
    def plot_net(self)  :
        import graphviz
        from IPython.display import display, Image

        dot = graphviz.Digraph(comment='Petri Net')
        
        # Add places
        for place in self.places.values():
            dot.node(place.uid, shape='circle', label=place.label, style='filled', fillcolor='lightgrey',fontsize='10')
        
        # Add transitions
        for transition in self.transitions.values():
            dot.node(transition.uid, shape='box', label=transition.label, style='filled', fillcolor='lightblue',fontsize='10')
        
        # Add arcs
        for place in self.places.values():

            for child in place.children:
                dot.edge(place.uid, child.uid)
 
        for transition in self.transitions.values():

            for child in transition.children:
                dot.edge(transition.uid,child.uid)
        
        dot_data = dot.pipe(format='png')
        display(Image(dot_data))
   
# %% Test
if __name__ == "__main__":
    
    benchmark='BU'
    instance_id="bu01"
    n_agv= 2
    
    petri=Petri_build(instance_id, benchmark=benchmark ,n_agv=n_agv) 
    petri.plot_net()
    
    
    




    
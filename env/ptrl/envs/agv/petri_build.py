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
        
        if  self.dynamic : 
            self.n_jobs,self.n_machines=size
        self.tran_durations = load_trans(self.n_machines,benchmark=benchmark)
        
        
        
        self.create_petri(LU=False ,show_flags=True)


    def __str__(self):
        """
        Get a string representation of the Petri net.
        Returns:
            str: A string representing the Petri net.
        """
        return f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines"

    def filter_nodes(self, node_role):
        """
        Filters nodes based on node type role.
        Parameters:
            node_role (str): role of nodes to filter.

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

    def node_info(self, node_uid,display=False):
        """
        Filters nodes based on nodeuid.
        Parameters:
            node_uid (str):

        Returns:
            object:the subject node.
        """
        for node in list (self.places.values())+list (self.transitions.values()):
            if node.uid == node_uid:  
                if display:
                    print(node) 
                return node

        print("node not found !")
                


    def add_nodes_layer(self, genre="place", type_="", role="", colored=True, timed=False,show=True,number=1):
        """
        Add a layer of nodes (places or transitions) to the Petri net.

        Parameters:
            is_place (bool): True if nodes are places, False if transitions.
            node_type (str): The type of nodes to be added place\transition.
            node_role (str): The role of nodes to be added  machine, job , source ....
            number (int): The number of nodes to be added.
        """
        if genre=="place":
            for i in range(number): 
                
                color = i if colored else None
                place_name = f"{role} {i}"
                place = Place(label=place_name,type_=type_,role= role,color=color,timed=timed ,show=show)   
                self.places[place.uid] = place   

        else:
            for i in range(number):
                color = i if colored else None
                transition_name = f"{role} {i}"
                transition = Transition( label = transition_name, type_=type_ , role =role, color=color, timed=timed ,show=show)  
                self.transitions[transition.uid] = transition


    def add_connection(self, parent_role, child_role, contype="p2t", fc=False):
        """
        Add connections (arcs) between nodes in the Petri net.

        Parameters:
            parent_type (str): The type of parent nodes.
            child_type (str): The type of child nodes.
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
                elif destination == None: #Unload
                     trans_time=int (self.tran_durations.iloc[origin+1][0])
                elif origin is not destination : # change of machine
                    trans_time=int (self.tran_durations.iloc[origin+1][destination+1])
                return trans_time
            
            except : 
                return 0
            
            
        for place in self.places.values():
            if place.type=="f":
                place.token_container.append(Token())

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
                    self.places[uid].token_container.append( Token(initial_place=uid, color=(job, None),
                                                                   process_time=time,
                                                                   order=i+1 ,
                                                                   trans_time= cal_time(current_machine,None),
                                                                   role="u"))         
            except : 
                pass # the reserve jobs are empty 


    def create_petri(self,LU=True ,show_flags=False):
        
        show_flags=show_flags
        
        
        #(genre=, type_=, role, colored timed,show,number)
        
 
        nodes_layers = [
            ("place", "f" ,  "job_idle",True, False,show_flags ,self.n_jobs) ,
            ("place", "b"  , "job", True, False,True , self.n_jobs),  
            ("trans", "c" ,  "job_select",False,False,True, self.n_jobs),
            ("place", "b" ,  "selected_jobs",False ,False,True, 1),
            
           
            ("trans", "c",  "agv_select",False,False,True,self.n_agv) ,  
            ("place", "p" , "agv_transporting",True,True,True,self.n_agv) ,
            ("place", "f" , "agv_idle",True,False,show_flags,self.n_agv) ,
            ("trans", "a",  "agv_finish",False,True,True,self.n_agv) , 
            
            
            ("place", "s" , "machine_sorting",False,False,True,1) ,
            ("trans", "a",  "machine_sort",True,False,True,self.n_machines),
            ("place", "b" , "machine_buffer",False,False,True, self.n_machines),
            ("trans", "c",  "machine_allocate",False,False,True,self.n_machines),
            ("place", "p" , "machine_processing",True,True,True, self.n_machines),
            ("place", "f" , "machine_idle",True,False,show_flags, self.n_machines),
            ("trans", "a",  "machine_finish",False,True,True,self.n_machines),
            ("place", "d" , "delivery",False,False, True,self.n_machines) ,
     
            
             
            ("place", "s" , "job_sorting",False,False, show_flags,1) ,
            ("trans", "a",  "job_sort",True,False,show_flags,self.n_jobs),
            ]


        layers_to_connect = [
            ("job_idle", "job_select", "p2t", False),
            ("job", "job_select", "p2t", False),
            ("job_select", "selected_jobs", "t2p", True),
            
            ("selected_jobs","agv_select","p2t", True),
            ("agv_idle","agv_select","p2t", False),
            ("agv_select","agv_transporting","t2p", False),   
            ("agv_transporting", "agv_finish", "p2t", False),
            ("agv_finish","agv_idle", "t2p", False),
            ("agv_finish", "machine_sorting", "t2p", True),
            
            ("machine_sorting", "machine_sort", "p2t", True), 
            ("machine_sort","machine_buffer", "t2p", False),
            ("machine_buffer", "machine_allocate", "p2t", False),
            ("machine_idle","machine_allocate", "p2t", False),
            ("machine_allocate", "machine_processing", "t2p", False),
            ("machine_processing", "machine_finish", "p2t", False),
            ("machine_finish","machine_idle", "t2p", False),
            ("machine_finish", "delivery", "t2p", False),
            ("machine_finish", "job_sorting", "t2p", True),
            ("job_sorting" ,"job_sort",  "p2t",True),
            ("job_sort", "job_idle", "t2p", False),
        ]
        
        
        if LU:
            
            nodes_layers += [ ("place", "p", "store", False,False,True, 1),("trans", "s", "lu", False,False,True,1)]
            layers_to_connect  += [("routing_2", "lu", "p2t", False), ("lu", "store", "t2p",False)]

        # Add nodes: places and transitions
        for genre, type_,role,colored,timed,show ,number in nodes_layers:
            self.add_nodes_layer(genre=genre,type_=type_,role=role,colored=colored, number=number ,timed=timed ,show=show)    

        # Add arcs places and transitions
        for parent_role, child_role, contype, full_connect in layers_to_connect:
            self.add_connection(parent_role, child_role, contype, full_connect)
            
        # Add jobs tokens
        self.add_tokens(LU)
         
        print (f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines, AGVs:{self.n_agv} , dynamic Mode: {self.dynamic}")
        
 
   
# %% Test
if __name__ == "__main__":
    
    benchmark='BU'
    instance_id="bu01"
    n_agv= 2
    
    petri=Petri_build(instance_id, benchmark=benchmark ,n_agv=n_agv) 

    
    
    




    
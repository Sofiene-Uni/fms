import copy 
from ptrl.envs.fms.petri_build import Petri_build
from ptrl.render.graph import  Graph
from ptrl.utils.obs_fms import get_obs


import warnings
warnings.filterwarnings("ignore", message=".*env.action_masks to get variables from other wrappers is deprecated.*")




class Simulator(Petri_build):
    """
    Class representing the core logic of a Job Shop Scheduling Problem (JSSP) simulation using a Petri net.

    Attributes:
        clock (int): The internal clock of the simulation.
        interaction_counter (int): Counter for interactions in the simulation.
        delivery_history (dict): Dictionary storing the delivery history.
        action_map (dict): Mapping for actions in the simulation from discrete to multidiscrete.

    Methods:
        __init__(instance_id, dynamic=False, size=(None,None), n_agv=2, n_tt=1):
            Initializes the JSSP simulator with optional parameters.

        petri_reset():
            Resets the internal state of the Petri net, including places and tokens.

        action_mapping():
            Maps multidiscrete actions to a dictionary for use with reinforcement learning.

        is_terminal():
            Checks if the simulation has reached a terminal state.

        sort_tokens():
            Processes tokens in sorting places based on their roles.

        refresh_state():
            Updates the state of the Petri net after sorting tokens and checking transitions.

        fire_timed():
            Advances simulation time and fires timed transitions based on elapsed times.

        action_masks():
            Checks which transitions are enabled for action selection.

        fire_controlled(action):
            Fires a controlled transition based on the provided action.

        time_tick():
            Increments the internal simulation clock and updates token logging.

        interact(action, screenshot=False):
            Performs Petri net interactions based on the action and updates internal state.
    """

    def __init__(self, 
                 label="main",
                 instance_id="ra01", 
                 layout=1,
                 n_agv=1,
                 n_tt=0,
                 
                 dynamic=False,
                 size=(None,None),
                 benchmark='Raj',
                 observation_depth=1,
                  ):
        """
    Initializes the JSSP simulator with the given parameters.

    Parameters:
        instance_id (str): Identifier for the JSSP instance.
        dynamic (bool): If True, allows appending new operations; termination condition is all queues empty.
        size (tuple): Size parameters for simulation only if dynamic  (default: (None, None)).
        n_agv (int): Number of AGVs (default: 2).
        n_tt (int): Number of tool transports (default: 1).
    """
    
        super().__init__(instance_id, 
                         layout= layout,
                         benchmark=benchmark,
                         n_agv=n_agv,
                         n_tt=n_tt,
                         dynamic=dynamic,
                         size=size,
                         )
        
        self.label=label
        self.create_petri(show_flags=True)
        self.print_instance_info()

        
        self.clock = 0
        self.interaction_counter = 0
        self.external_mask={}
        self.observation_depth=observation_depth
        
        self.delivery_history = {}
        self.action_map = self.action_mapping()
        self.graph=Graph(self)

        self.petri_reset()

        self.n_steps=0
        self.lookup_threshold=100e6
        self.total_deadhead=0
        

    def set_test_mode(self):
        self.lookup_threshold=100e6
        
    def print_instance_info (self): 
        if self.label=="main":
            print(f"{self.benchmark} Instance '{self.instance_id}' ,Layout: '{self.layout}' is loaded.")
            print(f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines X  {self.n_tools} Tools, AGVs: {self.n_agv}, TT: {self.n_tt}, Dynamic Mode: {self.dynamic}")
        
    def get_state(self):
         return get_obs(self,self.observation_depth)
     
        
    def  error_check(self):
        
        machine_check=  [p for p in self.places.values() if p.role=="machine_processing"] 
        job_check=  [p for p in self.places.values() if p.role=="job_idle"] 
        

        for check_point in machine_check:
            for token in check_point.token_container:
                if token.color[1]!=check_point.color:
                    print(f"error detected! {check_point.label} place color: {check_point.color} , token color: {token.color[1]}")
                    
        
        for check_point in job_check:
            for token in check_point.token_container:
                if token.color[0]!=check_point.color:
                    print(f"error detected! {check_point.label} place color: {check_point.color} , token color: {token.color[0]}")
        
        
        
    def petri_reset(self):
        """
        Resets the internal state of the Petri net, including the simulation clock and token containers in places.
        """
        self.clock = 0
        self.dead_heading=0
        
        for place in self.places.values():
            place.token_container = []
                  
        self.add_tokens()

    def action_mapping(self):
         """
         Maps multidiscrete actions to a more versatile Discrete format to use with exp DQN.
         Returns:
             dict: Mapping dictionary from action number  to transition object .
         """
         controllabe_transitions =[t for t in self.transitions.values() if t.type == "c"]
         mapping_dict = {index: value for index, value in enumerate(controllabe_transitions)}
         return mapping_dict


    def apply_external_mask(self):
        for transition in self.action_map.values():
            for key,value in self.external_mask.items():  
                if transition.color == key and  value[0] <= self.clock<= value[1]:
                    transition.enabled=False
                    
        for place in (p for p in self.places.values() if p.role == "machine_processing"):
            for key,value in self.external_mask.items():  
                if place.color == key and  value[0] <= self.clock<= value[1]:
                    place.enabled=False
                else :
                    place.enabled=True


    def is_terminal(self):
        """
        Checks if the simulation has reached a terminal state.
        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        # all places are empty except delivery and flages
        process_places=  [p for p in self.places.values() if p.type  not in ["d","f"] ]
        empty_process = all(len(p.token_container) == 0 for p in process_places)
        return empty_process
           
      
    def refresh_state(self):
        """
       Refreshes the state of the Petri net after sorting tokens and checking enabled transitions.
       """
        """
        Sorts tokens in sorting places based on their roles: 
            0: job, 1: machine, 2 :tools).
        """
        def process_tokens(place, color_criterion_index):
            if not  place.token_container:
                return 
            
            for token in place.token_container.copy():
                for transition in place.children:
                    if token.color[color_criterion_index] == transition.color:
                        transition.fire(self.instance,self.clock)
                        break
                else:
                    place.token_container.remove(token)
                    print(f"Token color :{token.color} destroyed in {place.role} - No compatible destination found!")
                        
        for place in (p for p in self.places.values() if p.type == "s"):
            if place.role == "job_sorting":
                process_tokens(place, 0)
            elif place.role in  ["machine_sorting", "machine_sorting_T"] :
                process_tokens(place, 1)
            elif place.role in  ["request_sorting" , "tools_sorting"]:
                process_tokens(place, 2)
                

        enabled_auto =[t for t in self.transitions.values() if t.type=="a"  and  t.check_state()]
        for transition in enabled_auto:  
            transition.fire(self.instance,self.clock)
                


    def perform_lookahead(self, agv_color,policy , max_steps=1):
        """
        Perform lookahead simulation using the provided policy.
        
        Parameters:
            agv_color: The color of the AGV.
            max_steps: Number of future steps to simulate.
        
        Returns:
            next_machine: The next machine to move to.
        """

        def check_buffer():
            buffer = [p for p in twin.places.values() if p.uid in twin.filter_nodes("agv_buffer") and p.color == agv_color][0]
            return len(buffer.token_container) == 0
        
        def check_queue():
            queue = [p for p in twin.places.values() if p.uid in twin.filter_nodes("jobs") + twin.filter_nodes("oprations_buffer") and p.token_container]
            return  queue
                

        step = 0
        twin = copy.deepcopy(self)
        twin.label = "twin"
        
        
        if policy and twin and  check_queue():
            
            while check_buffer() and  check_queue()  and step < max_steps:
                obs = twin.get_state()
                mask = twin.guard_function()
                action, _ = policy.predict(obs, action_masks=mask, deterministic=True)

                fired_transitions = twin.fire_controlled(action)
                
                for uid in fired_transitions:
                    if twin.transitions[uid].role == "agv_select" and twin.transitions[uid].color == agv_color:
                        next_machine = twin.transitions[uid].children[0].token_container[0].machine_sequence[0]
                        return next_machine

                while sum(twin.guard_function()) == 0:
                    twin.time_tick()
                    twin.fire_timed(policy,True)
                    twin.fire_timed(policy,True)
                    if twin.is_terminal():
                        break
                step += 1


    def get_deadheadings(self,place,policy):
        
        buffer = place.parents[0].parents[0]
        token = place.token_container[0]

        previous_location = place.history[-1]
        next_location=None

        if buffer.token_container:
            next_location = buffer.token_container[0].machine_sequence[0]
        

            
        elif self.n_steps >= self.lookup_threshold:    
            next_location = self.perform_lookahead(place.color,policy,50)
            
        
        dead_heading = self.instance.get_time(previous_location, next_location, time_type=1)
        
        if dead_heading > 0:
            place.history[-1] = next_location
            token.time_features[2] = dead_heading
            token.deadheadings.append((place.color, previous_location, next_location, self.clock, dead_heading))
            
            self.total_deadhead+=dead_heading



    def fire_timed(self,policy,twin =False ):
        """
       Advances the simulation time, fires timed transitions, and updates the state of the Petri net.
       Returns:
           list: List of UIDs of transitions that fired.
       """
       
        fired_transitions = []
        def process_tokens(place, time_criterion ):  
            if not place.token_container:
                return 
            
            transition = place.children[0]
            token = place.token_container[0]   
            
            elapsed_time = token.logging[place.uid][2]
            reference_time = token.time_features[time_criterion]
            
            if elapsed_time >= reference_time :
                if place.role in ["agv_transporting"] and not twin :    
                    self.get_deadheadings(place ,policy)
                
                
                transition.fire(self.instance,self.clock)
                fired_transitions.append(transition.uid)
    
        for place in (p for p in self.places.values() if p.type == "p"):   
            if place.role == "machine_processing":
                process_tokens(place, 0)
                
            elif place.role in ["agv_transporting"]:
                process_tokens(place, 1)
         
            elif place.role in ["agv_relocating"]:
                process_tokens(place, 2)
                 
        self.refresh_state()
        self.delivery_history[self.clock] = [ token for place in self.places.values() if place.type == "d" for token in place.token_container]
           
        return fired_transitions


    def guard_function(self):
        
        """
        Checks which transitions are enabled for action selection based on the current state.
        Returns:
            list: List of boolean masks indicating enabled transitions.
        """
        self.refresh_state()
        #self.apply_external_mask()
        
        mask =[t.check_state()  for t in self.transitions.values() if t.type == "c"]
        return mask   

    def fire_controlled(self, action):
        """
       Fires a colored transition based on the provided action if it is enabled.
       Parameters:
           action: Action to be performed.
       Returns:
           list: List containing the UID of the fired transition, or an empty list if no transition was fired.
       """
        fired_transitions=[]  
        transition = self.action_map[int(action)] 
        
        if all(parent.token_container for parent in transition.parents):
            transition.fire(self.instance,self.clock)
            fired_transitions.append(transition.uid)
        
        self.interaction_counter += 1 
        return fired_transitions
            
    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        for place in [p for p in self.places.values() if p.type =="p"]  :
            place.tick()
            
            
        #self.error_check()  #  useful in safe mode mode 
            

    def interact(self, action ,external_mask ,screenshot ,policy ):
        """
        Performs Petri net interactions based on the provided action and updates the internal state.
    
        Parameters:
            action: Action to be performed.
            screenshot (bool): If True, generates a plot of the Petri net after each interaction (default: False).
        """
        
        fired_controlled = self.fire_controlled(action)  
        self.graph.plot_net(fired_controlled) if screenshot else None
        
        while sum(self.guard_function()) == 0:  
            self.time_tick()
            fired_timed = self.fire_timed(policy)
            fired_timed = self.fire_timed(policy)
            
            self.graph.plot_net(fired_timed) if screenshot else None
            if self.is_terminal():
               break
           
      

if __name__ == "__main__":
    
    instance = "ra01"
    layout =1
    n_agv=2
    n_tt=0
    
    dynamic=True
    size=(10,4)
    
    petri = Simulator(instance_id= instance ,layout=layout, n_agv=n_agv, n_tt=n_tt, dynamic=dynamic , size= size) 
    petri.graph.plot_net()
    
    petri.print_instance_info()
    

    
    
 
    
  
    
    

  
    
    
 
    
  
    
    

  
    
    
    

    
   
    
    
 

    
    
    
    
    
    
    
    
    
   
    
    

    
    

    
    
    

        


    
import copy
from ptrl.envs.agv.petri_build import Petri_build
from ptrl.render.graph import  Graph


class Simulator(Petri_build):
    """
    Class representing the core logic of a Job Shop Scheduling Problem (JSSP) simulation using a Petri net.

    Attributes:
        clock (int): The internal clock of the simulation.
        interaction_counter (int): Counter for interactions in the simulation.
        delivery_history (dict): Dictionary storing the delivery history.
        action_map (dict): Mapping for actions in the simulation from discreate to multidiscreate.
    Methods:
        __init__(instanceID): Initializes the JSSPSimulator.
        time_tick(gui, action): Increments the internal clock and updates token logging.
        transfer_token(origin, destination, current_clock): Transfers a token from one place to another.
        fire_colored(action): Fires colored transitions based on the provided action.
        fire_timed(): Fires timed transitions based on completion times.
        petri_interact(gui, action): Performs Petri net interactions and updates internal state.
        petri_reset(): Resets the internal state of the Petri net.
        is_terminal(): Checks if the simulation has reached a terminal state.
        action_mapping(n_machines, n_jobs): Maps multidiscrete actions to a more usable format.
        action_masks(): Checks which allocations are enabled.
    """

    def __init__(self, 
                 instance_id, 
                 dynamic=False,
                 size=(None,None),
                 n_agv=2
                  ):
        """
        Initializes the JSSPSimulator.
        Parameters:
            instanceID (str): Identifier for the JSSP instance.
            dynamic (bool): If True, appending new operations is possible, and the termination condition is that all queues are empty.

            trans (bool) : if True the transport time between machines in taken into considiration
        """
        super().__init__(instance_id, 
                         dynamic=dynamic,
                         benchmark='BU',
                         size=size,
                         n_agv=n_agv,
                         )
        
        self.clock = 0
        self.interaction_counter = 0
        self.delivery_history = {}
        self.action_map = self.action_mapping()
        self.graph=Graph(self)
        
        self.petri_reset()
        #self.graph.plot_net()
       

    def petri_reset(self):
        """
        Resets the internal state of the Petri net.
        """
        self.clock = 0
        for place in self.places.values():
            place.token_container = []
                  
        self.add_tokens()
        self.refresh_state()
        

    def action_mapping(self):
         """
         Maps multidiscrete actions to a more versatile Discrete format to use with exp DQN.
         Returns:
             dict: Mapping dictionary from action number  to transition object .
         """
         controllabe_transitions =[t for t in self.transitions.values() if t.type == "c"]
         mapping_dict = {index: value for index, value in enumerate(controllabe_transitions)}
         return mapping_dict


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
           
                
    def action_masks(self):   
        self.refresh_state()
        mask =[t.enabled for t in self.transitions.values() if t.type == "c"]
        return mask
    
    
    def refresh_state(self):
        self.sort_tokens()
        for transition in self.action_map.values(): 
            transition.check_state()
            
            
    def sort_tokens(self):  
        
        for place in [p for p in self.places.values() if p.type == "s"]:
            if place.role == "job_sorting" and place.token_container:
                tokens_to_process = list(place.token_container)  # Create a copy of the token list to avoid modification issues
                for token in tokens_to_process:
                 
                    for transition in place.children:
                        if token.color[0] == transition.color: 
                            transition.fire(clock=self.clock)
                              
            elif place.role == "machine_sorting" and place.token_container:
                tokens_to_process = list(place.token_container)
                for token in tokens_to_process:
                    for transition in place.children:
                        if token.color[1] == transition.color:
                            transition.fire(clock=self.clock)
                       
                      
    def fire_auto(self):
        
        fired_transitions=[]
        for place in  [p for p in self.places.values() if p.type =="p" ]  :
            if place.token_container:
                token=place.token_container[0]
                _, _, elapsed_time = list(token.logging.items())[-1][-1]
                transition=place.children[0]
                
                if  place.role == "agv_transporting" and elapsed_time>= token.trans_time:
                    transition.fire(clock=self.clock)
                   
                elif place.role == "machine_processing" and elapsed_time>= token.process_time:
                    transition.fire(clock=self.clock)

                self.refresh_state()     
                fired_transitions.append(transition.uid)
                
                
        delivery =  [p for p in self.places.values() if p.type =="d"] 
        self.delivery_history[self.clock] = [token  for place in delivery for token in place.token_container ] 
          
        return  fired_transitions
    
    
    def fire_controlled(self, action):
        """
        Fires colored transitions based on the provided action.
        Parameters:
            action: Action to be performed.
        Returns:
            bool: True if a transition is fired, False otherwise.  
        """
        
        fire_transisions=[]  
        if action in  [index for index, value in enumerate(self.action_masks()) if value]:
            self.interaction_counter += 1 
            transition = self.action_map[int(action)] 
            transition.fire(clock=self.clock)
            self.refresh_state()
            
            fire_transisions.append(transition.uid)
 
        return fire_transisions
            

    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        for place in [p for p in self.places.values() if p.type =="p"]  :
            place.tick()
               

    def interact(self, action ,screenshot=False):
        """
        Performs Petri net interactions and updates internal state.
        Parameters:
            action: Action to be performed.
        """
    
        fired_controlled = self.fire_controlled(action) 
        self.graph.plot_net(fired_controlled) if screenshot else None

        while sum(self.action_masks()) == 0:
            self.time_tick()
   
            fired_auto = self.fire_auto()
            self.graph.plot_net(fired_auto) if screenshot else None

            
            if self.is_terminal():
               break
           

if __name__ == "__main__":
    
    petri = Simulator("bu01") 
    petri.graph.plot_net()
   
    
    
 

    
    
    
    
    
    
    
    
    
   
    
    

    
    

    
    
    

        


    
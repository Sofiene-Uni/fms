from ptrl.envs.fms.petri_build import Petri_build
from ptrl.render.graph import  Graph


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
                 instance_id, 
                 layout=1,
                 n_agv=2,
                 n_tt=1,
                 
                 dynamic=False,
                 size=(None,None),
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
                         benchmark='Raj',
                         n_agv=n_agv,
                         n_tt=n_tt,
                         dynamic=dynamic,
                         size=size,
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
        Resets the internal state of the Petri net, including the simulation clock and token containers in places.
        """
        self.clock = 0
        for place in self.places.values():
            place.token_container = []
                  
        self.add_tokens()
        self.refresh_state()
        # self.delivery_history = {}

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
           
  
    def sort_tokens(self): 
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
                    #print(f"Token color :{token.color} destroyed in {place.role} - No compatible destination found!")
                        
        # def dynamic_agv_sorting(place, color_criterion_index):
        #     if not  place.token_container:
        #         return
        #     for token in place.token_container.copy():
        #         for transition in place.children:
        #             if token.color[color_criterion_index] == transition.dynamic_color:
        #                 transition.fire(self.instance,self.clock)
        #                 transition.dynamic_color = None
        #                 break

        for place in (p for p in self.places.values() if p.type == "s"):
            if place.role == "job_sorting":
                process_tokens(place, 0)
            elif place.role in  ["machine_sorting", "machine_sorting_T"]:
                process_tokens(place, 1)
            elif place.role in  ["request_sorting" , "tools_sorting"]:
                process_tokens(place, 2)
            elif place.role in ["next_job_sorting"]:
                process_tokens(place, 0)
            # elif place.role in ["agv_request_sorting"]:
            #     dynamic_agv_sorting(place, 3)

            elif place.role in ["agv_request_sorting"]:
                process_tokens(place, 3)
    

    def refresh_state(self):
        """
       Refreshes the state of the Petri net after sorting tokens and checking enabled transitions.
       """
        fired_transitions = []
        # self.dynamic_agv_colors()
        self.sort_tokens()
        fired_transitions.extend(self.fire_automatic())

        for transition in self.action_map.values(): 
            transition.check_state()
        return fired_transitions

    def fire_timed(self):
        """
       Advances the simulation time, fires timed transitions, and updates the state of the Petri net.
       Returns:
           list: List of UIDs of transitions that fired.
       """

        fired_transitions = []
        
        def process_tokens(place, time_criterion):
            if not place.token_container:
                return 
            
            transition = place.children[0]
            token = place.token_container[0]      
            # elapsed_time = token.logging[place.label][2]
            elapsed_time = token.logging[place.uid][2]
            
            if elapsed_time >=token.time_features[time_criterion] :
                transition.fire(self.instance,self.clock)
                fired_transitions.append(transition.label)
    

        for place in (p for p in self.places.values() if p.type == "p"):  
            
            if place.role == "machine_processing":
                process_tokens(place, 0)
                
            elif place.role in ["agv_transporting"]:
                process_tokens(place, 1)
                
            elif place.role in [ "tool_transporting"]:
                 process_tokens(place, 2)

            elif place.role in ["agv_dead_heading"]:
                process_tokens(place, 3)

            elif place.role in ["tool_transport_dead_heading"]:
                process_tokens(place, 4)
                

        fired_transitions.extend(self.refresh_state())
        
        self.delivery_history[self.clock] = [
            token for place in self.places.values() if place.type == "d" for token in place.token_container
        ]
    
        return fired_transitions


    def action_masks(self):
        
        """
        Checks which transitions are enabled for action selection based on the current state.
        Returns:
            list: List of boolean masks indicating enabled transitions.
        """
        
        self.refresh_state()
        mask =[t.enabled for t in self.transitions.values() if t.type == "c"]
        return mask   
        

    def fire_controlled(self, action):
        """
       Fires a colored transition based on the provided action if it is enabled.
       Parameters:
           action: Action to be performed.
       Returns:
           list: List containing the UID of the fired transition, or an empty list if no transition was fired.
       """
        
        fire_transitions=[]  
     
        transition = self.action_map[int(action)] 
        
        if all(parent.token_container for parent in transition.parents):
            transition.fire(self.instance,self.clock)
            fire_transitions.append(transition.label)
        
        self.refresh_state()
        self.interaction_counter += 1 
 
        return fire_transitions
            

    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        for place in [p for p in self.places.values() if p.type =="p"]  :
            place.tick()
               

    def interact(self, action ,screenshot=False):
        """
        Performs Petri net interactions based on the provided action and updates the internal state.
    
        Parameters:
            action: Action to be performed.
            screenshot (bool): If True, generates a plot of the Petri net after each interaction (default: False).
        """
        if self.clock == 0:
            self.delivery_history = {}
        fired_controlled = self.fire_controlled(action)  
        self.graph.plot_net(fired_controlled) if screenshot else None

        places = list(self.places.values())
        transitions = list(self.transitions.values())
        places.extend(transitions)
        places.sort(key=lambda x: int(x.uid))
        print("controlled", fired_controlled) if len(fired_controlled) else None
        i = 0
        while sum(self.action_masks()) == 0:
            fired_timed = self.fire_timed()
            self.graph.plot_net(fired_timed) if screenshot else None
            self.time_tick()


            i += 1
            # print(i)
            if self.is_terminal():
               break
            print("timed", fired_timed) if len(fired_timed) else None

    def fire_automatic(self):

        trans_fired = []
        for trans in [trans for trans in self.transitions.values() if trans.role in ["agv_start"]]:
            if all(parent.token_container for parent in trans.parents):
                # print("There")
                trans.fire(self.instance, self.clock)
                trans_fired.append(trans.label)
        return trans_fired

    # def dynamic_agv_colors(self):
    #
    #     for place in [place for place in self.places.values() if place.role == "agv_waiting"]:
    #         if place.token_container:
    #             dynamic_color = place.token_container[0].color[0]
    #             place_color = place.color
    #             for agv_request_sorting in [place for place in self.places.values() if place.role == "agv_request_sorting"]:
    #                 if agv_request_sorting.color == place_color:
    #                     agv_request_sorting.dynamic_color = dynamic_color
    #                     break


if __name__ == "__main__":
    
    petri = Simulator("ra01") 
    petri.graph.plot_net()
    places = list(petri.places.values())
    transitions = list(petri.transitions.values())
    places.extend(transitions)
    places.sort(key=lambda x: int(x.uid))
    for p in places:
        print(p.uid, p)
 

    
    
    
    
    
    
    
    
    
   
    
    

    
    

    
    
    

        


    
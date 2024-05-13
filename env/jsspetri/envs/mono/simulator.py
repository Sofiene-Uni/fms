import copy
from jsspetri.common.petri_build import Petri_build

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
                 standby=False):
        """
        Initializes the JSSPSimulator.

        Parameters:
            instanceID (str): Identifier for the JSSP instance.
            dynamic (bool): If True, appending new operations is possible, and the termination condition is that all queues are empty.
        """
        super().__init__(instance_id, 
                         dynamic=dynamic,
                         standby=standby)

        self.clock = 0
        self.interaction_counter = 0
        self.delivery_history = {}
        self.jobs,self.select,self.ready,self.allocate,self.machines, self.deliver,self.delivery  = [], [], [], [], [] ,[], []
        self.petri_reset()
        
        self.action_map = self.action_mapping(self.n_machines, self.n_jobs)
       

    def petri_reset(self):
        """
        Resets the internal state of the Petri net.
        """
        self.clock = 0
        for place in self.places.values():
            place.token_container = []
        self.add_tokens()
   
    
        self.jobs = [p for p in self.places.values() if p.uid in self.filter_nodes("job")]
        self.select = [p for p in self.transitions.values() if p.uid in self.filter_nodes("select")]
        self.ready = [p for p in self.places.values() if p.uid in self.filter_nodes("ready")]
        self.allocate = [t for t in self.transitions.values() if t.uid in self.filter_nodes("allocate")]
        self.machines = [p for p in self.places.values() if p.uid in self.filter_nodes("machine")]
        self.deliver = [t for t in self.transitions.values() if t.uid in self.filter_nodes("finish_op")]
        self.delivery = [p for p in self.places.values() if p.uid in self.filter_nodes("finished_ops")]
        
        

    def action_mapping(self, n_machines, n_jobs):
         """
         Maps multidiscrete actions to a more versatile Discrete format to use with exp DQN.

         Parameters:
             n_machines (int): Number of machines.
             n_jobs (int): Number of jobs.

         Returns:
             dict: Mapping dictionary.
         """
         tuples = []
         mapping_dict = {}

         for machine in range(n_machines):
             for job in range(n_jobs):
                 tuple_entry = (job, machine)
                 tuples.append(tuple_entry)
                 index = len(tuples) - 1
                 mapping_dict[index] = tuple_entry
                 
         if self.standby :
             idle = {len(mapping_dict.keys()): (None,None)}
             mapping_dict.update(idle)

         return mapping_dict
    

    def utilization_reward(self):
        """
        Calculates the utilization reward.

        Returns:
            float: Calculated reward.
        """
                
        idle_machines = sum(1 for machine in self.machines if machine.enabled)
        x = - (idle_machines / self.n_machines)
        return x


    def is_terminal(self, step=0):
        """
        Checks if the simulation has reached a terminal state.

        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        empty_queue = all(len(p.token_container) == 0 for p in self.jobs)
        empty_machines = all(len(p.token_container) == 0 for p in self.machines) 
        return empty_queue and empty_machines
    
  
    def valid_action(self,action):
        valid=False
        job_idx,machine_idx=self.action_map[int(action)]
       
        if job_idx==None:
            return True    
        else :  
            
           if  self.jobs[job_idx].token_container:
            token = self.jobs[job_idx].token_container[0]
            machine = self.machines[machine_idx]
            
            color = token.color[1] == machine.color
            machine = self.machines[machine_idx].enabled
            precedence = self.jobs[job_idx].enabled  
            
            if color and machine and precedence:
                valid= True
                    
        return valid
    
    
    def action_masks(self):
        actions = range(len (self.action_map))
        enabled_mask = list(map (self.valid_action, actions))
        
      
        return enabled_mask
        

    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        self.safeguard()
        
        for machine in self.machines:
                if  machine.token_container:
                    token = machine.token_container[0]
                    last_logging = list(token.logging.keys())[-1]
                    token.logging[last_logging][2] += 1


    def transfer_token(self, origin, destination, clock=0):
        """
        Transfers a token from one place to another.

        Parameters:
            origin: Origin place.
            destination: Destination place.
            current_clock (int): Current simulation clock.
        """
        
        if not origin.token_container:# place empty 
            return False

        token = copy.copy(origin.token_container[0])
        destination.token_container.append(token)
        origin.token_container.pop(0)

        token.logging[origin.uid][1] = clock
        token.logging[destination.uid] = [clock, 0, 0]

        return True

    def safeguard(self):
        for machine in self.machines:
            if machine.token_container:
                token=machine.token_container[0]
                if machine.color != token.color[1] :
                    print(f"error detected { (machine.color, token.color[1])}")
                   

    def fire_allocate(self, action):
        """
        Fires colored transitions based on the provided action.

        Parameters:
            action: Action to be performed.

        Returns:
            bool: True if a transition is fired, False otherwise.
        """
        self.interaction_counter += 1
        job_idx, machine_idx = self.action_map[int(action)] 
        
        if job_idx == None :
            return True  #handle standby action
        
        elif action in [index for index, value in enumerate(self.action_masks()) if value]: 
            
            selected= self.transfer_token(self.jobs[job_idx], self.ready[job_idx], self.clock)    
            allocated = self.transfer_token(self.ready[job_idx], self.machines[machine_idx], self.clock)   
            
            self.jobs[job_idx].enabled = False
            self.machines[machine_idx].enabled = False 
            return selected and allocated
        
        else:
            return False
       

    def fire_timed(self):
        """
        Fires autonomous transitions based on completion times.
        """
        fired = False
        
        for  machine in self.machines: 
            if machine.token_container:
                token = machine.token_container[0]
                _, _, elapsed_time = list(token.logging.items())[-1][-1]
                if  elapsed_time> token.process_time  :
                    self.transfer_token(machine, self.delivery[machine.color], self.clock)
                    self.jobs[token.color[0]].enabled = True
                    self.machines[token.color[1]].enabled = True 
                    fired = True
                    
        self.time_tick()          
        self.delivery_history[self.clock] = [token for place in self.delivery for token in place.token_container]
        
        return fired

    def interact(self, action):
        
        """
        Performs Petri net interactions and updates internal state.

        Parameters:
            action: Action to be performed.
        """

        fired=self.fire_allocate(action)
        #allocation does not advance time (decision step) ,-choosen standby does  
        if action == list(self.action_map.keys())[-1] and self.standby:
            self.fire_timed()

        # Only the idle is enabled (no action available)
        while sum(self.action_masks()) == int (self.standby):
            self.fire_timed()
            if self.is_terminal():
                break
            
        return fired

if __name__ == "__main__":
    
    pass
    
    

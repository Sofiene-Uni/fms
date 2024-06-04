import copy
from jsspetri.common.petri_build import Petri_build

class Simulator_AGV(Petri_build):
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
                 standby=False,
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
                         standby=standby,
                         benchmark='BU',
                         size=size,
                         n_agv=n_agv
                         )
        
        self.clock = 0
        self.interaction_counter = 0
        self.delivery_history = {}
        self.jobs,self.agvs,self.buffer,self.select,self.ready,self.allocate,self.machines, self.deliver,self.delivery  = [], [], [], [], [] ,[], [],[],[]
        self.petri_reset()

        self.action_map = self.action_mapping(self.n_machines, self.n_jobs ,self.n_agv )
       

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
        self.agvs = [p for p in self.places.values() if p.uid in self.filter_nodes("agv")]
        self.buffer = [p for p in self.transitions.values() if p.uid in self.filter_nodes("transport")]
        self.ready = [p for p in self.places.values() if p.uid in self.filter_nodes("ready")]
        self.store = [p for p in self.places.values() if p.uid in self.filter_nodes("store")]
        self.allocate = [t for t in self.transitions.values() if t.uid in self.filter_nodes("allocate")]
        self.machines = [p for p in self.places.values() if p.uid in self.filter_nodes("machine")]
        self.deliver = [t for t in self.transitions.values() if t.uid in self.filter_nodes("finish_op")]
        self.delivery = [p for p in self.places.values() if p.uid in self.filter_nodes("finished_ops")]
        

    def action_mapping(self, n_machines, n_jobs , n_agv):
         """
         Maps multidiscrete actions to a more versatile Discrete format to use with exp DQN.

         Parameters:
             n_machines (int): Number of machines.
             n_jobs (int): Number of jobs.

         Returns:
             dict: Mapping dictionary.
         """

         mapping_dict = {}
         index =0
         
         for machine in range(n_machines):
            mapping_dict[index] = (machine, machine)
            index+=1
            
            
         for job in range(n_jobs):
            for avg in range (n_agv):
                mapping_dict[index] = (job,avg)
                index+=1
         return mapping_dict


    def utilization_reward(self):
        """
        Calculates the utilization reward.

        Returns:
            float: Calculated reward.
        """
                
        idle_machines = sum(1 for machine in self.machines if machine.busy)
        x = - (idle_machines / self.n_machines)
        return x

    def safeguard(self):
        for machine in self.machines:
            if machine.token_container:
                token=machine.token_container[0]
                if machine.color != token.color[1] :
                    print(f"error detected { (machine.color, token.color[1])}")


    def print_state(self):
        print(f"Clock: {self.clock}")
        print("******current state**********") 
        print("")
        print(f"jobs:     {[len(p.token_container) for p in self.jobs]}" )
        print( f"agv:      {[len(p.token_container) for p in self.agvs]}")
        print(f"ready:    {[len(p.token_container) for p in self.ready]}",f"store:{[len(p.token_container) for p in self.store]}")
        print(f"machines: {[len(p.token_container) for p in self.machines]}")
        print (f"delivery: {[len(p.token_container) for p in self.delivery]}")
        print("")
        print(f"jobs busy:     {[p.busy for p in self.jobs]}" )
        print( f"agv busy:      {[p.busy for p in self.agvs]}")
        print(f"ready busy: {[p.busy for p in self.ready]}")
        print(f"machines busy: {[p.busy for p in self.machines]}")

        print("")
        print (f"action mask : {self.action_masks()}")
        
        
    def is_terminal(self, step=0):
        """
        Checks if the simulation has reached a terminal state.
        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        empty_queue = all(len(p.token_container) == 0 for p in self.jobs)
        empty_agvs = all(len(p.token_container) == 0 for p in self.agvs) 
        empty_buffer = all(len(p.token_container) == 0 for p in self.ready) 
        empty_machines = all(len(p.token_container) == 0 for p in self.machines) 

        return empty_queue and empty_buffer  and empty_machines  and empty_agvs
    
  
    def valid_action(self,action):
        
        valid = False
        origin,destination=self.action_map[int(action)]
        
        if action < self.n_machines:  #allocate : 
        
            if self.ready [origin].token_container :   
                token = self.ready[origin].token_container[0]
      
                ready =  self.ready[origin].busy    # a token is ready to be allocated 
                color = token.color[1] == self.machines[destination].color
                machine = not self.machines[destination].busy
                valid =  color and machine and ready 
                
                
        else  :   #transport 
            if self.jobs[origin].token_container  and not self.jobs[origin].busy and not self.agvs[destination].busy :
                valid =True   # enabled if a token is available and the job is not being processed 

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
        
        for place in self.jobs+ self.ready + self.machines + self.agvs:
                if  place.token_container:
                    token = place.token_container[0]
                    last_logging = list(token.logging.keys())[-1]
                    token.logging[last_logging][2] += 1   # elapsed time increament 
                        
        for place in self.ready :
            if  place.token_container:
                place.busy=True
            else :
                place.busy=False
                     

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
        token.current_place=destination.color
        

        destination.token_container.append(token)
        origin.token_container.pop(0)

        token.logging[origin.uid][1] = clock
        token.logging[destination.uid] = [clock, 0, 0]
        return True


    def fire_controlled(self, action):
        """
        Fires colored transitions based on the provided action.

        Parameters:
            action: Action to be performed.

        Returns:
            bool: True if a transition is fired, False otherwise.
        """
        
        self.interaction_counter += 1  
        origin, destination = self.action_map[int(action)] 
        
        if action in [index for index, value in enumerate(self.action_masks()) if value]: 
            
            if action < self.n_machines :    #allocate
                allocated = self.transfer_token(self.ready[origin], self.machines[destination], self.clock)  
                self.machines[destination].busy = True 
                return allocated

            else : #transport
                transported= self.transfer_token(self.jobs[origin], self.agvs[destination], self.clock) 
                self.jobs[origin].busy= True
                self.agvs[destination].busy= True
                return transported
            
        else :
            return False 
        

    def fire_timed(self):
        """
        Fires autonomous transitions based on completion times.
        """

        for  place  in self.machines +self.agvs  : 
            if place.token_container:
                token = place.token_container[0]
                _, _, elapsed_time = list(token.logging.items())[-1][-1]
                
                if  place.type == "agv" and elapsed_time>= token.trans_time:
                    
                    if token.type=="op":
                        self.transfer_token(place, self.ready[token.color[1]], self.clock)
                        self.agvs[token.current_place].busy = False   #AGV is available 
                        
                    elif token.type=="u" : # unload token 
                        self.transfer_token(place, self.store[0], self.clock)
                        self.agvs[token.current_place].busy = False   #AGV is available 
                        self.jobs[token.color[0]].busy = False    #Job is available 
                        
              
                elif  place.type == "machine" and elapsed_time>= token.process_time  :    
                    self.transfer_token(place, self.delivery[place.color], self.clock)
                    self.jobs[token.color[0]].busy = False
                    self.machines[token.color[1]].busy = False
                    
        self.delivery_history[self.clock] = [token for place in self.delivery for token in place.token_container] + [token for place in self.store for token in place.token_container]
        
        if sum(self.action_masks()) == 0:
            self.time_tick()          
      
        
  
    def interact(self, action):
        """
        Performs Petri net interactions and updates internal state.
        Parameters:
            action: Action to be performed.
        """

        #self.print_state()
        fired=self.fire_controlled(action)  

        while sum(self.action_masks()) == 0:
            self.fire_timed()
            if self.is_terminal():
                break
            
        return fired


if __name__ == "__main__":
    
    petri = Simulator_AGV("bu01") 
    petri.print_state()
    
    
    for token in petri.jobs[0].token_container:
        print(token)
        

        
        
    

  




    

    
    
            
    
  

    


    
    

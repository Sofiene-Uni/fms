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
                 benchmark = "Taillard",
                 trans_layout = None,
                 dynamic=False,
                 standby=False,
                 trans=True):
        """
        Initializes the JSSPSimulator.

        Parameters:
            instanceID (str): Identifier for the JSSP instance.
            dynamic (bool): If True, appending new operations is possible, and the termination condition is that all queues are empty.

            trans (bool) : if True the transport time between machines in taken into considiration

        """
        super().__init__(instance_id,
                         benchmark = benchmark,
                         trans_layout = trans_layout,
                         dynamic=dynamic,
                         standby=standby,
                         trans=trans)
        # self.i = 0
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
         
         for job in range(n_jobs):
             mapping_dict[job] = (job,job)
             

         for machine in range(n_machines):
             for job in range(n_jobs):
                 tuple_entry = (job, machine)
                 tuples.append(tuple_entry)
                 index = n_jobs+ len(tuples) - 1
                 mapping_dict[index] = tuple_entry

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
        print("******current state**********")
        print( [p.busy for p in self.jobs])
        print( [p.busy for p in self.machines])
        print( [len(p.token_container) for p in self.jobs])
        print([len(p.token_container) for p in self.ready])
        print ([len(p.token_container) for p in self.machines])
        print ([len(p.token_container) for p in self.delivery])
        print (self.action_masks())


    def is_terminal(self, step=0):
        """
        Checks if the simulation has reached a terminal state.

        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        empty_queue = all(len(p.token_container) == 0 for p in self.jobs)
        empty_transit = all(len(p.token_container) == 0 for p in self.ready) 
        empty_machines = all(len(p.token_container) == 0 for p in self.machines) 
       
        return empty_queue and empty_transit  and empty_machines 
    
  
    def valid_action(self,action):
        # print(self.i) if self.i < 500 else None
        valid = False
        origin,destination=self.action_map[int(action)]
        
        
        if action < self.n_jobs:  #select :     
            if self.jobs[origin].token_container  and not self.jobs[origin].busy:
                valid =True   # enabled if a token is available and the job is not being processed 
            
        else  :   #allocate 

            if self.ready [origin].token_container :   
                token = self.ready[origin].token_container[0]
      
                ready =  self.ready[origin].busy    # a token is ready to be allocated
                color = token.color[1] == self.machines[destination].color
                machine = not self.machines[destination].busy
                
                valid =  color and machine and ready 
                
        return valid 
                
            

    def action_masks(self):
        actions = range(len (self.action_map))
        enabled_mask = list(map (self.valid_action, actions))
        # self.i += 1
        return enabled_mask
        

    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        self.safeguard()
        
        for place in self.jobs+ self.ready + self.machines:
                if  place.token_container:
                    token = place.token_container[0]
            
                    last_logging = list(token.logging.keys())[-1]
                    token.logging[last_logging][2] += 1   # elapsed time increament 


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
        print((origin, destination))
        
        if action in [index for index, value in enumerate(self.action_masks()) if value]: 
            
            if action < self.n_jobs :        #select
               selected= self.transfer_token(self.jobs[origin], self.ready[destination], self.clock) 
               self.jobs[origin].busy= True
               return selected
            else :                           #allocate 
                allocated = self.transfer_token(self.ready[origin], self.machines[destination], self.clock)  
                self.ready[origin].busy = False
                self.machines[destination].busy = True 
                
                return allocated
            
        else :
            return False 
        

    def fire_timed(self):
        """
        Fires autonomous transitions based on completion times.
        """

        for place in self.machines + self.ready:
            if place.token_container:
                token = place.token_container[0]
                _, _, elapsed_time = list(token.logging.items())[-1][-1]

                # if  place.type == "machine" and elapsed_time> token.process_time  :
                # The jobs shall finish right when the elapsed time is equal to process times
                if place.type == "machine" and elapsed_time >= token.process_time:
                    self.transfer_token(place, self.delivery[place.color], self.clock)
                    self.jobs[token.color[0]].busy = False
                    self.machines[token.color[1]].busy = False

                # elif  place.type == "ready" and elapsed_time> token.trans_time:
                # The tokens shall be ready right when the elapsed time is equal to process times
                elif place.type == "ready" and elapsed_time > token.trans_time:
                    self.ready[token.color[0]].busy = True   # token is available

        self.delivery_history[self.clock] = [token for place in self.delivery for token in place.token_container]
        # If delivery is done, at least one ready will be free, thus more valid actions, without ticking the time
        if sum(self.action_masks()) == 0:
            self.time_tick()

  
    def interact(self, action):
        
        """
        Performs Petri net interactions and updates internal state.

        Parameters:
            action: Action to be performed.
        """

        fired=self.fire_controlled(action)
        # print(self.action_masks())
        while sum(self.action_masks()) == 0:
            self.fire_timed()
            if self.is_terminal():
                break

        return fired

if __name__ == "__main__":
    
    petri = Simulator("bu01")

    
    print( [len(p.token_container) for p in petri.jobs])
    print([len(p.token_container) for p in petri.ready])
    print ([len(p.token_container) for p in petri.machines])


    print (petri.action_masks())
    print (petri.action_map)


    # for job in  petri.jobs :
    #     for op in job.token_container :
    #         print(op)




    

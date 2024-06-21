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
        
        self.routing_1,self.routing_2=[],[]
        self.jobs ,self.job_select ,self.lu , self.store = [],[],[],[]
        self.avg_select , self.agv_process , self.agv_finish =[],[],[]
        self.machine_select ,self.machine_buffer ,self.machine_allocate ,self.machines_process ,self.machine_finish ,self.machine_delivery= [],[],[],[],[],[]
   
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
        self.add_tokens(LU=True)
   
        self.jobs = [p for p in self.places.values() if p.uid in self.filter_nodes("job")]
        self.job_select = [t for t in self.transitions.values() if t.uid in self.filter_nodes("job_select")]   
        
        self.routing_1=  [p for p in self.places.values() if p.uid in self.filter_nodes("routing_1")]
        
        self.avg_select = [t for t in self.transitions.values() if t.uid in self.filter_nodes("avg_select")]
        self.agv_process = [p for p in self.places.values() if p.uid in self.filter_nodes("agv_process")]
        self.agv_finish = [t for t in self.transitions.values() if t.uid in self.filter_nodes("agv_finish")]
        
        self.routing_2= [p for p in self.places.values() if p.uid in self.filter_nodes("routing_2")]      
        
        self.machine_sort = [t for t in self.transitions.values() if t.uid in self.filter_nodes("machine_sort")]
        self.machine_buffer = [p for p in self.places.values() if p.uid in self.filter_nodes("machine_buffer")]
        self.machine_allocate = [t for t in self.transitions.values() if t.uid in self.filter_nodes("machine_allocate")] 
        self.machine_process = [p for p in self.places.values() if p.uid in self.filter_nodes("machine_process")]
        self.machine_finish = [t for t in self.transitions.values() if t.uid in self.filter_nodes("machine_finish")]
        self.machine_delivery = [p for p in self.places.values() if p.uid in self.filter_nodes("machine_delivery")]
        
        self.lu = [t for t in self.transitions.values() if t.uid in self.filter_nodes("lu")]
        self.store = [p for p in self.places.values() if p.uid in self.filter_nodes("store")]
        
        
        self.check_valid()
        

    def action_mapping(self):
         """
         Maps multidiscrete actions to a more versatile Discrete format to use with exp DQN.

         Parameters:
             n_machines (int): Number of machines.
             n_jobs (int): Number of jobs.

         Returns:
             dict: Mapping dictionary.
         """

         controllabe_transitions =[t for t in self.transitions.values() if t.type == "c"]
         mapping_dict = {index: value for index, value in enumerate(controllabe_transitions)}
         
         # print(controllabe_transitions)
         # for uid in controllabe_transitions : 
         #     self.node_info(uid)

         return mapping_dict


    def utilization_reward(self):
        """
        Calculates the utilization reward.

        Returns:
            float: Calculated reward.
        """
                
        idle_machines = sum(1 for machine in self.machine_process if machine.busy)
        x = - (idle_machines / self.n_machines)
        return x

    def safeguard(self):
        for machine in self.machine_process:
            if machine.token_container:
                token=machine.token_container[0]
                if machine.color != token.color[1] :
                    print(f"error detected { (machine.color, token.color[1])}")


    def print_state(self):
        print(f"Clock: {self.clock}")
        print("******current state**********") 
        print("")
        print(f"jobs:     {[len(p.token_container) for p in self.jobs]}" )
        print( f"agv:      {[len(p.token_container) for p in self.agv_process]}")
        print(f"machine buffer:    {[len(p.token_container) for p in self.machine_buffer]}",f"store:{[len(p.token_container) for p in self.store]}")
        print(f"machines process : {[len(p.token_container) for p in self.machine_process]}")
        print (f"machine delivery: {[len(p.token_container) for p in self.machine_delivery]}")
        print("")
        
        print(f"jobs busy:     {[p.busy for p in self.jobs]}" )
        print( f"agv busy:      {[p.busy for p in self.agv_process]}")
        print(f"ready busy: {[p.busy for p in self.machine_buffer]}")
        print(f"machines busy: {[p.busy for p in self.machines_process]}")
        print("")

        
        
    def is_terminal(self):
        """
        Checks if the simulation has reached a terminal state.
        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        # all places other than the delivery places empty 
        process_places= self.machine_select = [p for p in self.places.values() if p.uid  not in self.filter_nodes("machine_delivery")] 
        empty_process = all(len(p.token_container) == 0 for p in process_places)
        return empty_process
    
  
    def check_valid(self):
        
        
        #initiate state to non enabled
        for trans in self.action_map.values() :
            trans.enabled=False
            
 
        for transition in self.action_map.values():  
            parent=transition.parents[0]
            
            if transition.parents[0].token_container:
                token=transition.parents[0].token_container[0] 

            
            if transition.type=="c" :   # controllable transitions
               if parent.token_container  and  parent.enabled :   
                   if transition.color==None :     # not colored
                       transition.enabled=True
                       
                   elif   transition.color==token.color: # colored 
                       transition.enabled=True


            else  :   # automatic transitions  transition.type=="a"
            
                pass
       
          
    def action_masks(self):
        mask =[t.enabled for t in self.transitions.values() if t.type == "c"]
        return mask
    
    
    
    
        
    # def time_tick(self):
    #     """
    #     Increments the internal clock and updates token logging.
    #     """
    #     self.clock += 1
    #     self.safeguard()
        
    #     for place in self.jobs+ self.ready + self.machines + self.agvs:
    #             if  place.token_container:
    #                 token = place.token_container[0]
    #                 last_logging = list(token.logging.keys())[-1]
    #                 token.logging[last_logging][2] += 1   # elapsed time increament 
                        
    #     for place in self.ready :
    #         if  place.token_container:
    #             place.busy=True
    #         else :
    #             place.busy=False
                     

    # def transfer_token(self, origin, destination, clock=0):
    #     """
    #     Transfers a token from one place to another.

    #     Parameters:
    #         origin: Origin place.
    #         destination: Destination place.
    #         current_clock (int): Current simulation clock.
    #     """
        
    #     if not origin.token_container:# place empty 
    #         return False

    #     token = copy.copy(origin.token_container[0])
    #     token.current_place=destination.color
        

    #     destination.token_container.append(token)
    #     origin.token_container.pop(0)

    #     token.logging[origin.uid][1] = clock
    #     token.logging[destination.uid] = [clock, 0, 0]
    #     return True


    # def fire_controlled(self, action):
    #     """
    #     Fires colored transitions based on the provided action.

    #     Parameters:
    #         action: Action to be performed.

    #     Returns:
    #         bool: True if a transition is fired, False otherwise.
    #     """
        
    #     self.interaction_counter += 1  
    #     origin, destination = self.action_map[int(action)] 
        
    #     if action in [index for index, value in enumerate(self.action_masks()) if value]: 
            
    #         if action < self.n_machines :    #allocate
    #             allocated = self.transfer_token(self.ready[origin], self.machines[destination], self.clock)  
    #             self.machines[destination].busy = True 
    #             return allocated

    #         else : #transport
    #             transported= self.transfer_token(self.jobs[origin], self.agvs[destination], self.clock) 
    #             self.jobs[origin].busy= True
    #             self.agvs[destination].busy= True
    #             return transported
            
    #     else :
    #         return False 
        

    # def fire_timed(self):
    #     """
    #     Fires autonomous transitions based on completion times.
    #     """

    #     for  place  in self.machines +self.agvs  : 
    #         if place.token_container:
    #             token = place.token_container[0]
    #             _, _, elapsed_time = list(token.logging.items())[-1][-1]
                
    #             if  place.role == "agv" and elapsed_time>= token.trans_time:
                    
    #                 if token.role=="op":
    #                     self.transfer_token(place, self.ready[token.color[1]], self.clock)
    #                     self.agvs[token.current_place].busy = False   #AGV is available 
    #                     self.ready[token.color[1]].busy = True
                        
    #                 elif token.role=="u" : # unload token 
    #                     self.transfer_token(place, self.store[0], self.clock)
    #                     self.agvs[token.current_place].busy = False   #AGV is available 
    #                     self.jobs[token.color[0]].busy = False    #Job is available 
                        
              
    #             elif  place.role == "machine" and elapsed_time>= token.process_time  :    
    #                 self.transfer_token(place, self.delivery[place.color], self.clock)
    #                 self.jobs[token.color[0]].busy = False
    #                 self.machines[token.color[1]].busy = False
                    
    #     self.delivery_history[self.clock] = [token for place in self.delivery for token in place.token_container] + [token for place in self.store for token in place.token_container]

    # def interact(self, action):
    #     """
    #     Performs Petri net interactions and updates internal state.
    #     Parameters:
    #         action: Action to be performed.
    #     """
    #     # self.print_state()
    #     # print(self.clock, action, self.action_map[int(action)])
    #     fired = self.fire_controlled(action)
    #     while sum(self.action_masks()) == 0:
    #         if self.is_terminal():
    #             break
    #         self.time_tick()
    #         self.fire_timed()
    #     return fired


if __name__ == "__main__":
    
    petri = Simulator("bu01") 
    
    #petri.print_state()

    petri.graph.plot_net()
    
    print( petri.action_map)
    
    

    
    

    
    
    

        


    
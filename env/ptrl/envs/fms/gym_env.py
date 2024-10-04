import numpy as np
from gymnasium import Env
from gymnasium import spaces

from ptrl.envs.fms.simulator import Simulator
from ptrl.render.plot_fms import plot_solution,plot_job


class FmsEnv(Env):
    
    """
    Custom Gym environment for Job Shop Scheduling using a Petri net simulator.
    """
    metadata = {"render_modes": ["solution" , "human"]}

    def __init__(self, 
                 
                 benchmark :str="Raj",
                 instance_id :str="ra01" ,
                 layout:int =1,
                 n_agv:int =1,
                 n_tt:int =0, # tool transport
                 
                 dynamic: bool=False,
                 size=(None,None),
                 
                 observation_depth:int = 1 , 
                 reward_f:str="G",
                 render_mode: str ="solution",
                 
                 ):
        """
        Initializes the JsspetriEnv.
        if the JSSP is flexible a maximum number of machines and jobs if predefined regardless le instance size 

        Parameters:
            render_mode (str): Rendering mode ("human" or "solution").
            instance_id (str): Identifier for the JSSP instance.
            observation_depth (int): Depth of observations in future.
        """
        
        self.dynamic=dynamic
        self.instance_id=instance_id
        
        self.sim = Simulator(instance_id=self.instance_id,layout=layout,n_agv=n_agv ,n_tt=n_tt ,dynamic=self.dynamic, size=size ,benchmark=benchmark ,observation_depth=observation_depth)


        observation_size= self.sim.n_jobs + 2*(self.sim.n_jobs*observation_depth)+ 4*self.sim.n_agv + (self.sim.n_agv*self.sim.n_machines)+ 2*self.sim.n_tt+  3*self.sim.n_machines  
        
        self.observation_space= spaces.Box(low=-1, high=self.sim.max_bound,shape=(observation_size,),dtype=np.int64)
        self.action_space = spaces.Discrete(len(self.sim.action_map))  
      
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.reward_f=reward_f
        self.min_makespan=100000
        
        self.policy=None
        
    def reset(self, seed=None, options=None):
        """
        Reset the environment.
        Returns:
            tuple: Initial observation and info.
        """
        self.sim.petri_reset()
        observation=self.sim.get_state()
        info = self._get_info(0,False,False)
        return observation, info
    
    def reward(self,diffrence=0,terminal=False):
        """
        Calculate the reward.
        Parameters:
            terminal: if the episode reached termination.
        Returns:
            Any: Calculated reward .
        """

        def calculate_utilization(role, max_resources):
           idle_places = [p for p in self.sim.places.values() if p.uid in self.sim.filter_nodes(role)]
           idle_resource = sum(1 for resource in idle_places if resource.token_container)
           utilization = - (idle_resource / max_resources)
           return utilization
       
        
        if self.reward_f=="G":
            if terminal :  
                if self.sim.clock < self.min_makespan :
                    self.min_makespan=self.sim.clock
                    print(self.min_makespan)
                return -self.sim.clock 
            else :
                return 0
            
         
        elif self.reward_f=="M":
            return   calculate_utilization("machine_idle", self.sim.n_machines)
        elif self.reward_f=="A":
            return   calculate_utilization("agv_idle", self.sim.n_agv)
        elif self.reward_f=="T":
            return   calculate_utilization("tool_idle", self.sim.n_tt)
   

    def action_masks(self):
        """
        Get the action masks.
        Returns:
            list: List of enabled actions.
        """ 
        return self.sim.guard_function()
    
    def step(self, action ,external_mask=None ):
        """
        Take a step in the environment.
        Parameters:
            action: Action to be performed.
        Returns:
            tuple: New observation, reward, termination status, info.
            
        """
        
        screenshot= True if self.render_mode == "human" else False
        
        diffrence = self.sim.interact(action,external_mask=external_mask,screenshot=screenshot , policy=self.policy)  
        observation = self.sim.get_state()
        terminated= self.sim.is_terminal()
        reward = self.reward(diffrence,terminated)
        info = self._get_info()
        return observation, reward, terminated, False, info
    

    def render(self,show_rank=False ,job_zoom=False,format_="png",dpi=300):
        """
        Render the environment.
        """
        if self.render_mode ==  "solution":
            plot_solution(self.sim,show_rank=show_rank,format_=format_,dpi=dpi)
            if job_zoom :
                for i in range (self.sim.n_jobs):
                    plot_job(self.sim,job=i,format_=format_,dpi=dpi)
                    
        if self.render_mode == "human":
            plot_solution(self.sim,show_rank=show_rank,format_=format_,dpi=dpi)
            # lunch GUI to display imag sequence , TO DO 
 

    def close(self):
        """
        Close the environment.
        """

    def _get_info(self, reward=0,fired=False, terminated=False):
        """
        Get information dictionary.
        """
        return {"Reward": reward,"Fired":fired ,"Terminated": terminated ,"mask":self.sim.guard_function()}

if __name__ == "__main__":
    
    instance="ra01"
    agvs=2
    tools_transport=1
    
    dynamic, size=False ,(6,4)
    env=FmsEnv(instance_id=instance,dynamic=dynamic,size=size,n_agv=agvs ,n_tt=tools_transport)
    
    
    observation,info=env.reset()
    


    

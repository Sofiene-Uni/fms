import numpy as np
from gymnasium import Env
from gymnasium import spaces

from ptrl.envs.fms.simulator import Simulator
from ptrl.render.plot_fms import plot_solution,plot_job
from ptrl.utils.obs_fms import get_obs


class FmsEnv(Env):
    
    """
    Custom Gym environment for Job Shop Scheduling using a Petri net simulator.
    """
    metadata = {"render_modes": ["solution" , "human"]}

    def __init__(self, 
                
                 instance_id :str ,
                 layout:int =1,
                 n_agv=1,
                 n_tt=0, # tool transport
                 
                 observation_depth:int =1, 
                 dynamic: bool=False,
                 size=(None,None),
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
        
        self.sim = Simulator(self.instance_id,layout=layout,n_agv=n_agv ,n_tt=n_tt ,dynamic=self.dynamic, size=size)
        self.observation_depth = min(observation_depth, self.sim.n_machines)
   
        # observation_size= 2*self.sim.n_machines +2*self.sim.n_agv+2*self.sim.n_tt+ 2*(self.sim.n_jobs * self.observation_depth) +1
        observation_size = 3 * self.sim.n_jobs + (self.sim.n_machines + self.sim.n_agv)
        self.observation_space= spaces.Box(low=-1, high=self.sim.max_bound,shape=(observation_size,),dtype=np.int64)
    
    
        self.action_space = spaces.Discrete(len(self.sim.action_map))  
      
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode


    def reset(self, seed=None, options=None):
        """
        Reset the environment.
        Returns:
            tuple: Initial observation and info.
        """
        self.sim.petri_reset()
        observation = get_obs(self)
        info = self._get_info(0,False,False)

        return observation, info

    def reward(self,terminal):
        """
        Calculate the reward.
        Parameters:
            terminal: if the episode reached termination.
        Returns:
            Any: Calculated reward .
        """
        
        def utilization_reward(self):
            """
            Calculates the utilization reward/penalty.
            Returns:
                float: Calculated feedback.
            """   
            
            def calculate_utilization(role, max_resources):
               idle_places = [p for p in self.sim.places.values() if p.uid in self.sim.filter_nodes(role)]
               idle_resource = sum(1 for resource in idle_places if resource.token_container)
               utilization = - (idle_resource / max_resources)
               return utilization

            machine_util = calculate_utilization("machine_idle", self.sim.n_machines)
            agv_util = calculate_utilization("agv_idle", self.sim.n_agv)
            
            return (machine_util + agv_util) / 2
        
    
        #return utilization_reward(self)
        
        if terminal :
            return -self.sim.clock
        else :
            return 0

    def action_masks(self):
        """
        Get the action masks.
        Returns:
            list: List of enabled actions.
        """ 
        return self.sim.action_masks()
    
    def step(self, action):
        """
        Take a step in the environment.
        Parameters:
            action: Action to be performed.
        Returns:
            tuple: New observation, reward, termination status, info.
        """
        fired = self.sim.interact(action,screenshot= True if self.render_mode == "human" else False)  
        observation = get_obs(self)
        terminated= self.sim.is_terminal()
        reward = self.reward(terminated)
        info = self._get_info(reward,fired,terminated)
        
        return observation, reward, terminated, False, info

    def render(self,n_agv=0,n_tt=0,job_zoom=False,format_="png",dpi=300):
        """
        Render the environment.
        """
        rank=False
        if self.render_mode ==  "solution":
            plot_solution(self.sim,n_agv=n_agv,n_tt=n_tt,show_rank=rank,format_=format_,dpi=dpi)
            if job_zoom :
                for i in range (self.sim.n_jobs):
                    plot_job(self.sim,job=i,format_=format_,dpi=dpi)
                    
        
        if self.render_mode == "human":
            plot_solution(self.sim,n_agv=n_agv,n_tt=n_tt,show_rank=rank,format_=format_,dpi=dpi)
            # lunch GUI to display imag sequence , TO DO 
 
                    
   
    def close(self):
        """
        Close the environment.
        """

    def _get_info(self, reward,fired, terminated):
        """
        Get information dictionary.
        """
        return {"Reward": reward,"Fired":fired ,"Terminated": terminated}

if __name__ == "__main__":
    
    instance="ra01"
    agvs=2
    tools_transport=1
    
    dynamic, size=False ,(6,4)
    env=FmsEnv(instance_id=instance,dynamic=dynamic,size=size,n_agv=agvs ,n_tt=tools_transport)

    

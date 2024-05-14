import numpy as np
from gymnasium import Env
from gymnasium import spaces

from jsspetri.envs.fms.simulator import Simulator
from jsspetri.render.plot_fms import plot_solution, plot_job
from jsspetri.utils.obs_fms import get_obs


class FmsEnv(Env):
    """
    Custom Gym environment for Job Shop Scheduling using a Petri net simulator.
    """
    metadata = {"render_modes": ["solution"]}

    def __init__(self, 
                 instance_id :str ,
                 render_mode: bool =None,
                 observation_depth:int =1, 
                 dynamic: bool=False,
                 standby:bool=False,
              
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

        self.sim = Simulator(self.instance_id,dynamic=self.dynamic,standby=standby)
        self.observation_depth = min(observation_depth, self.sim.n_machines)
   
         
        observation_size= 3 * self.sim.n_machines + 2 * (self.sim.n_jobs * self.observation_depth)  
        self.observation_space= spaces.Box(low=-1, high=self.sim.max_bound,shape=(observation_size,),dtype=np.int64)
        self.action_space = spaces.Discrete(len (self.sim.jobs)*len(self.sim.machines)+len (self.sim.jobs))  # select and allocate combinations
      
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

    def reward(self,action):
        """
        Calculate the reward.
        Parameters:
            advantage: Advantage given by the interaction.
        Returns:
            Any: Calculated reward .
        """
        
        return self.sim.utilization_reward()
    

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
        

        fired = self.sim.interact(action)  
        reward = self.reward(action)
        observation = get_obs(self)
        terminated= self.sim.is_terminal()
        info = self._get_info(reward,fired,terminated)
        
        return observation, reward, terminated, False, info

    def render(self,zoom=False ,rank=False,format_="png",dpi=300):
        """
        Render the environment.
        """
        if self.render_mode == "solution":
             
            if zoom :
                for i in range (self.sim.n_jobs):
                    plot_job(self.sim,job=i,format_=format_,dpi=dpi)
                    
            plot_solution(self.sim,show_rank=rank,format_=format_,dpi=dpi)
       

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
    
    env=FmsEnv("ta01",dynamic=False)
    
    print (env.action_space)
 
  
    
    

    
   

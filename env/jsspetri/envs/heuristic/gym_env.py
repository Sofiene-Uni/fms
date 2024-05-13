import numpy as np
from gymnasium import Env
from gymnasium import spaces

from jsspetri.envs.heuristic.simulator import Simulator
from jsspetri.render.plot_mono import plot_solution
from jsspetri.utils.obs_mono import get_obs


class HeuristicEnv(Env):
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

        self.action_space = spaces.Discrete(len(self.sim.heuristics))   #number of heuristics
      
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
            advantage: Advantage given by the interaction.
        Returns:
            Any: Calculated reward .
        """
        if terminal :
            return -self.sim.clock
        else :
            return 0

    def step(self, action):
        """
        Take a step in the environment.
        Parameters:
            action: Heuristic rule for dispatch .
        Returns:
            tuple: New observation, reward, termination status, info.
        """
        fired = self.sim.interact(action)  
        terminated= self.sim.is_terminal()
        reward = self.reward(terminated)
        observation = get_obs(self)
        info = self._get_info(reward,fired,terminated)
        
        return observation, reward, terminated, False, info

    def render(self,rank=False,format_="png",dpi=300):
        """
        Render the environment.
        """
        if self.render_mode == "solution":
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
    
    def action_info(self,action):
        """
        Parameters
        ----------
        action : TYPE
            DESCRIPTION.
        Returns
        -------
        TYPE "string"
            returns information on the heuristic used.
        """
        return  self.sim.heuristics[action]
    
if __name__ == "__main__":
    env=HeuristicEnv("ta01")
    
 

    
  
    
    

    
   

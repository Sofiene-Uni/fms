import numpy as np
from gymnasium import Env
from gymnasium import spaces

from jsspetri.envs.multi.simulator import Simulator
from jsspetri.render.plot_multi import plot_solution
from jsspetri.utils.obs_muli import get_obs


class MultiEnv(Env):
    """
    Custom Gym environment for Job Shop Scheduling using a Petri net simulator.
    """
    metadata = {"render_modes": ["solution"]}

    def __init__(self, render_mode=None,
                 instance_id="ta01",
                 dynamic=False,
                 standby=True,
                 observation_depth=1,
                 weights=[0.5,0.5]
                 ):
        """
        Initializes the JsspetriEnv.
        if the JSSP is dynamic a maximum number of machines and jobs if predefined regardless le instance size 

        Parameters:
            render_mode (str): Rendering mode ("human" or "solution").
            instance_id (str): Identifier for the JSSP instance.
            observation_depth (int): Depth of observations in future.
        """
        
        self.weights=weights
        self.dynamic=dynamic
        self.standby=standby
        self.instance_id=instance_id

        self.sim = Simulator(self.instance_id,dynamic=self.dynamic,standby=standby)
        self.observation_depth = min(observation_depth, self.sim.n_machines)
  
        
        observation_size= 4 * self.sim.n_machines + 2 * (self.sim.n_jobs * self.observation_depth)  +1
        self.observation_space= spaces.Box(low=-1, high=self.sim.max_bound,shape=(observation_size,),dtype=np.int64)
        self.action_space = spaces.Discrete(len (self.sim.action_map))   
     
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode


   

    def reset(self, seed=None, options=None):
        """
        Reset the environment.

        Returns:
            tuple: Initial observation and info.
        """
        self.sim.petri_reset()
        observation =  get_obs(self)
        info = self._get_info(0, False)
        
        return observation, info

    def reward(self,terminal,env_feedbacks, weights):
        reward = sum(weight * objectif for weight, objectif in zip(weights, env_feedbacks)) 
        #print(f"Current reward is {reward}")
        return reward

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
  
        env_feedbacks = self.sim.interact(action)   
        terminated = self.sim.is_terminal()
        reward = self.reward(terminated ,env_feedbacks,self.weights)
        observation =  get_obs(self)
        info = self._get_info(reward, terminated)
        
        return observation, reward, terminated, False, info

    def render(self,rank=False):
        """
        Render the environment.
        """
        if self.render_mode == "solution":
            plot_solution(self.sim, self.weights,show_rank=rank)
       

    def close(self):
        """
        Close the environment.
        """
     
    def _get_info(self, reward, terminated):
        """
        Get information dictionary.

        Parameters:
            reward: Current reward.
            terminated (bool): Termination status.

        Returns:
            dict: Information dictionary.
        """
        return {"Reward": reward, "Terminated": terminated}

if __name__ == "__main__":
    
    env= MultiEnv()
    
    obs= get_obs(env)
    
    print(obs)

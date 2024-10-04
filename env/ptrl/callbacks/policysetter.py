from stable_baselines3.common.callbacks import BaseCallback

class PolicyCallback(BaseCallback):
    def __init__(self, env, verbose=0):
        super(PolicyCallback, self).__init__(verbose)  # Correct usage of super()
        self.env = env

    def _on_rollout_start(self):
        # This method is called before the rollout starts (i.e., at the beginning of an episode)
        self.env.policy = self.model.policy
        if self.verbose > 0:
            print("Policy has been set in the environment at the start of the episode.")
            
            
    def _on_step(self):
        
        #self.env.sim.n_steps+=1
     
        return True  # Continue training
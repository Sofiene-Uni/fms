import  os
import ptrl
import time
import gymnasium as gym
from datetime import datetime
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
from ptrl.render.plot_fms import plot_solution

class SaveBestModelCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every `check_freq` steps).
    Based on https://stable-baselines3.readthedocs.io/en/master/guide/callbacks.html
    """

    def __init__(self,verbose=1):
        super(SaveBestModelCallback, self).__init__(verbose)
        # self.save_path = save_path
        self.best_makespan = np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        # if self.save_path is not None:
        #     os.makedirs(self.save_path, exist_ok=True)
        pass
    def _on_step(self) -> bool:
        # Check that the number of steps taken is a multiple of `check_freq`
        simulation = self.training_env.envs[0].sim
        if self.training_env.buf_infos[0]['Terminated']:
            if self.training_env.buf_infos[0]['Clock'] < self.best_makespan:
                self.best_makespan = self.training_env.buf_infos[0]['Clock']
                print(f"Best makespan of {self.best_makespan} achieved at timestep {self.model.num_timesteps}")
                spec_string = f"{simulation.instance_id}_{simulation.layout}_{simulation.n_agv}_{simulation.n_tt}_{self.model.num_timesteps}"
                self.model.save(f"agents/Best_Agent_{spec_string}.zip")
                plot_solution(simulation,
                              simulation.n_agv,
                              simulation.n_tt,
                              filename=f"Best_Solution_{spec_string}",
                              show = False)
        # self.model.save(os.path.join(self.save_path, 'best_model'))
        return True

def train_jssp(instance_id,layout=2,n_agv=2 ,n_tt=1,timesteps=100000,dynamic=False,size=(None,None),render_mode="solution"):
    env = gym.make("ptrl-fms-v0",
                   render_mode=render_mode,
                   instance_id=instance_id,
                   layout=layout,
                   n_agv=n_agv,
                   n_tt=n_tt,
                   dynamic=dynamic,
                   size=size,
    ).unwrapped
    
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    log_file = f"logs/Log_{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}_{current_datetime}.zip"
    model = MaskablePPO("MlpPolicy", env, 
                        ent_coef=0.01,
                        verbose=1,
                        seed=101,
                        tensorboard_log=log_file
                        )

    start_time = time.time()  
    model.learn(total_timesteps=timesteps, callback=SaveBestModelCallback())
    end_time = time.time()  
    elapsed_time = end_time - start_time  
  
        
    # Check if the 'info' file exists
    if os.path.exists('0-info.txt'):
        with open('0-info.txt', 'a') as info_file:
            info_file.write(f" {current_datetime} -The total {instance_id} training time (seconds): {elapsed_time}\n")
    else:
        with open('0-info.txt', 'w') as info_file:
            info_file.write(f" {current_datetime} -The total {instance_id} training time (seconds): {elapsed_time}\n")
      
    print(f"Training took {elapsed_time} seconds")
    model.save(f"agents/Agent_{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}.zip")

def main():
    
    # instances= ["ra01","ra02","ra03","ra04","ra05","ra06","ra07","ra08","ra09","ra10"]
    instances= ["ra01"]
    layout=2
    n_agv=2
    n_tt=1
    
    timesteps =3e5
    dynamic,size=False,(10,5)
    render_mode="solution"
    
    for instance_id  in  instances :
        train_jssp(instance_id,layout,n_agv=n_agv ,n_tt=n_tt,timesteps=timesteps,dynamic=dynamic,size=size,render_mode=render_mode)

if __name__ == "__main__":
    main()

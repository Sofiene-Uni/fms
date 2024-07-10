import  os
import ptrl
import time
import gymnasium as gym
from datetime import datetime
from sb3_contrib import MaskablePPO


def train_jssp(instance_id,layout=1,n_agv=1 ,n_tt=0,timesteps=100000,dynamic=False,size=(None,None),render_mode="solution"):
    env = gym.make("ptrl-fms-v0",
                   render_mode=render_mode,
                   instance_id=instance_id,
                   layout=layout,
                   n_agv=n_agv,
                   n_tt=n_tt,
                   dynamic=dynamic,
                   size=size,
    ).unwrapped
    
    
    model = MaskablePPO("MlpPolicy", env, 
                        ent_coef=0.01,
                        verbose=1,
                        seed=101,
                        tensorboard_log="logs"
                        )

    start_time = time.time()  
    model.learn(total_timesteps=timesteps)
    end_time = time.time()  
    elapsed_time = end_time - start_time  
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    
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
    
    instances= ["ra01"]
    layout=1
    n_agv=2
    n_tt=0
    
    timesteps =1e5
    dynamic,size=False,(10,5)

    render_mode="solution"
    
    for instance_id  in reversed (instances) :
        train_jssp(instance_id,layout,n_agv=n_agv ,n_tt=n_tt,timesteps=timesteps,dynamic=dynamic,size=size,render_mode=render_mode)

if __name__ == "__main__":
    main()
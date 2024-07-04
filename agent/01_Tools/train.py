import  os
import ptrl
import gymnasium as gym
from sb3_contrib import MaskablePPO
import time
from datetime import datetime


#tensorboard_log="logs"


def train_jssp(instance_id, timesteps=100000,dynamic=False,size=(None,None),n_agv=2 , n_tt=1 ,render_mode="solution"):
    env = gym.make("ptrl-tools-v0",
                   render_mode=render_mode,
                   instance_id=instance_id,
                   dynamic=dynamic,
                   size=size,
                   n_agv=n_agv,
                   n_tt=n_tt,
                  
                   
    ).unwrapped
    
    
    model = MaskablePPO("MlpPolicy", env, 
                        ent_coef=0.01,
                        verbose=1,
                        seed=101,

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
    model.save(f"agents/MaskablePPO-{instance_id}-{n_agv}-{n_tt}-{timesteps}.zip")

def main():
    

    
    instances= ["ra01"]
    timesteps =1e5
    dynamic,size=False,(10,5)

    n_agv=2
    n_tt=2
    
    render_mode="solution"
    
    for instance_id  in reversed (instances) :
        train_jssp(instance_id, timesteps=timesteps,dynamic=dynamic,size=size ,n_agv=n_agv ,n_tt=n_tt ,render_mode=render_mode)

if __name__ == "__main__":
    main()
import  os
import jsspetri
import gymnasium as gym
from sb3_contrib import MaskablePPO
import time
from datetime import datetime


#tensorboard_log="logs"


def train_jssp(instance_id, timesteps=100000,dynamic=False,size=(None,None),n_agv=2):
    env = gym.make("jsspetri-fms-v0",
                   render_mode="solution",
                   instance_id=instance_id,
                   dynamic=dynamic,
                   size=size,
                   n_agv=n_agv
    ).unwrapped
    
    
    model = MaskablePPO("MlpPolicy", env, verbose=1,seed=101,tensorboard_log="logs", learning_rate=0.0001)

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
    model.save(f"agents/MaskablePPO-{instance_id}-{n_agv}-{timesteps}.zip")

def main():
    instances = ["bu01", "bu02", "bu03", "bu04", "bu05", "bu06", "bu07", "bu08", "bu09", "bu10"]
    timesteps = 500000
    dynamic = False
    size = [(6, 4), (7, 4), (7, 4), (6, 4), (6, 4), (7, 4), (9, 4), (7, 4), (6, 4), (7, 4)]
    n_agv = 2
    # agent_id=f"{instance_id}-{n_agv}"

    for i in [2, 3, 5, 6, 7, 9]:
        train_jssp(instances[i], timesteps=timesteps,dynamic=dynamic,size=size[i] ,n_agv=n_agv)

if __name__ == "__main__":
    main()
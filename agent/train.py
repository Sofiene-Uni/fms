import  os
import jsspetri
import gymnasium as gym
from sb3_contrib import MaskablePPO
import time
from datetime import datetime


#tensorboard_log="logs"


def train_jssp(instance_id, benchmark = 'Taillard', trans = True, trans_layout = None, timesteps=100000,dynamic=False):
    env = gym.make("jsspetri-fms-v0",
                   render_mode="solution",
                   instance_id=instance_id,
                   benchmark=benchmark,
                   trans_layout = trans_layout,
                   trans= trans,
                   dynamic=dynamic,
    ).unwrapped
    
    
    model = MaskablePPO("MlpPolicy", env, verbose=1,seed=101,tensorboard_log="logs")

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
    model.save(f"agents/MaskablePPO-{instance_id}-{timesteps}.zip")

def main():

    #instances= ["ta11","ta21","ta61","ta01"]
    # instances= ["ta01"]
    # timesteps = 100000
    # benchmark = "Taillard"
    #
    # for instance_id  in instances :
    #     train_jssp(instance_id, benchmark=benchmark, trans_layout='trans_15', timesteps=timesteps)
    instances = ["bu01"]
    timesteps = 100000
    benchmark = "BU"
    trans = True
    trans_lay = 'trans_4_1'

    for instance_id in instances:
        train_jssp(instance_id, benchmark=benchmark, trans = trans, trans_layout=trans_lay, timesteps=timesteps)


if __name__ == "__main__":
    main()
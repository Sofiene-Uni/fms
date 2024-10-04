import os
import time
import gymnasium as gym
from datetime import datetime
from sb3_contrib import MaskablePPO
from stable_baselines3.common.env_util import make_vec_env
from ptrl.callbacks.policysetter import PolicyCallback

def train_jssp_multi_agent(render_mode="solution",
                           benchmark="Raj",
                           instance_id="ra01",
                           layout=1,
                           n_agv=1,
                           n_tt=0,
                           timesteps=1e5,
                           dynamic=False,
                           size=(None, None),
                           reward_f="G",
                           n_envs=4):  # Number of environments for multi-agent training
    # Create a vectorized environment with multiple agents
    env = make_vec_env(lambda: gym.make("ptrl-fms-v0",
                                        render_mode=render_mode,
                                        benchmark=benchmark,
                                        instance_id=instance_id,
                                        layout=layout,
                                        n_agv=n_agv,
                                        n_tt=n_tt,
                                        dynamic=dynamic,
                                        size=size,
                                        reward_f=reward_f
                                        ).unwrapped,
                       n_envs=n_envs)  # Number of parallel environments

    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")

    log_file = f"logs/Log_{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}_{current_datetime}.zip"
    
   
      
    model = MaskablePPO(
            "MlpPolicy",
            env,
            learning_rate=3e-4, 
            ent_coef=0.01,  
            clip_range=0.1,  
            n_steps=2000, 
            verbose=1,
            #tensorboard_log=log_file,
            policy_kwargs=dict(
                net_arch=dict(pi=[512*10, 256*10, 128*10], vf=[512*10, 256*10, 128*10])) 
            )


    start_time = time.time()

    policy_callback = PolicyCallback(env)
    model.learn(total_timesteps=timesteps, callback=policy_callback)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Log training time
    if os.path.exists('0-info.txt'):
        with open('0-info.txt', 'a') as info_file:
            info_file.write(f" {current_datetime} - Instance {instance_id}_{layout}_{n_agv}_{n_tt}:  training time: {elapsed_time} ,Minimum makespan :{env.get_attr('min_makespan')} \n")
    else:
        with open('0-info.txt', 'w') as info_file:
            info_file.write(f" {current_datetime} - Instance {instance_id}_{layout}_{n_agv}_{n_tt}:  training time: {elapsed_time} ,Minimum makespan :{env.get_attr('min_makespan')} \n")


    model.save(f"agents/Agent_{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}_{reward_f}_D.zip")
    print(env.get_attr('min_makespan'))  # Adjusted to use get_attr for VecEnv
    

def main():
    benchmark = "Raj"
    n_agv = 2
    n_tt = 0

    # instances = ["ra02", "ra04", "ra06", "ra07", "ra08", "ra09", "ra10", "ra01", "ra03", "ra05"]
    # layouts = [2, 3, 4,1]
    
    
    instances = ["ra01"]
    layouts = [1]

    timesteps = 5e5
    dynamic, size = True, (10, 5)
    render_mode = "solution"
    reward_f = "G"
    n_envs = 4  # Define number of environments for multi-agent training

    for layout in layouts:
        for instance_id in instances:
            train_jssp_multi_agent(render_mode=render_mode,
                                   benchmark=benchmark,
                                   instance_id=instance_id,
                                   layout=layout,
                                   n_agv=n_agv,
                                   n_tt=n_tt,
                                   timesteps=timesteps,
                                   dynamic=dynamic,
                                   size=size,
                                   reward_f=reward_f,
                                   n_envs=n_envs)

if __name__ == "__main__":
    main()

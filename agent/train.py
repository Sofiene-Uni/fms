import  os
import ptrl
import time
import gymnasium as gym
from datetime import datetime
from sb3_contrib import MaskablePPO
from ptrl.callbacks.policysetter import PolicyCallback


def train_jssp( render_mode="solution",
                benchmark="Raj",
                instance_id="ra01",
                layout=1,
                n_agv=1 ,
                n_tt=0,
                timesteps=1e5,
                dynamic=False,
                size=(None,None),
                reward_f= "G"
               ):
    
    env = gym.make("ptrl-fms-v0",
                   render_mode=render_mode,
                   benchmark=benchmark,
                   instance_id=instance_id,
                   layout=layout,
                   n_agv=n_agv,
                   n_tt=n_tt,
                   dynamic=dynamic,
                   size=size,
                   reward_f=reward_f
    ).unwrapped
    
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    log_file = f"logs/Log_{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}_{current_datetime}.zip"
    model = MaskablePPO("MlpPolicy", env, 
                        learning_rate= 3e-4,
                        clip_range=0.2,
                        ent_coef=0.1,
                        n_steps=2048,
                        verbose=1,
                        #seed=101,
                        tensorboard_log=log_file
                        )

    start_time = time.time()  
    
    policy_callback = PolicyCallback(env)
    model.learn(total_timesteps=timesteps,callback=policy_callback)
    
    
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
    model.save(f"agents/Dynamic_{benchmark}_{size[0]}_{size[1]}_{n_agv}_M.zip")
    
    print(env.min_makespan)

def main():
    
    benchmark="Raj"
    n_agv=2
    n_tt=0

    # instances= ["ra02","ra04","ra06","ra07","ra08","ra09","ra10","ra01","ra03","ra05"]
    #layouts=[1,2,3,4]
    
    instances= ["ra02"]
    layouts=[1]

    timesteps =3e5
    dynamic,size=True,(10,8)
    render_mode="solution"
    reward_f="G"
    
    
    for layout in layouts:
        for instance_id  in  instances :
            train_jssp(render_mode=render_mode,
                       benchmark=benchmark,
                       instance_id=instance_id,
                       layout=layout,
                       n_agv=n_agv ,
                       n_tt=n_tt,
                       timesteps=timesteps,
                       dynamic=dynamic,
                       size=size,
                       reward_f=reward_f
                       )

if __name__ == "__main__":
    main()
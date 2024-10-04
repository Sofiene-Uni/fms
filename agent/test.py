import copy 
import time
import ptrl
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks


#%% create environement 


def agent_test(benchmark="Raj",agent_id="ra01",instance="ra01",layout=1,n_agv=1,n_tt=0,dynamic = False ,size=(None,None) ,render_mode="solution"):
    
    local_agent = f"agents/Agent_{agent_id}.zip"
    global_agent= f"agents/Dynamic_{benchmark}_{size[0]}_{size[1]}_{n_agv}.zip"
    
    env = gym.make("ptrl-fms-v0",
                   render_mode=render_mode,
                   benchmark=benchmark,
                   instance_id=instance_id,
                   layout=layout,
                   n_agv=n_agv,
                   n_tt=n_tt,
                   dynamic=dynamic,
                   size=size,   
    ).unwrapped
    

    model = MaskablePPO.load(global_agent) if dynamic else MaskablePPO.load(local_agent)
    i,terminated,(obs,info)=0,False,env.reset()
    start_time = time.time() 
    
    env.policy=model.policy
    env.sim.set_test_mode()
    
 
    while not terminated :    
        env_masks = get_action_masks(env)
        action, _states = model.predict(obs, action_masks=env_masks,deterministic=True)
        obs, reward, terminated, truncated,info= env.step(action)
        i+=1 
        
    end_time = time.time()
    elapsed_time = end_time - start_time   
    
    
    env.render(show_rank=True ,job_zoom=False)
    
    print(f" inference took {elapsed_time} seconds") 
    print(f" Makespan : {env.sim.clock} , number of interactions {env.sim.interaction_counter}")
    return env.sim.clock


if __name__ == "__main__":

    benchmark="Raj"
    instance_id= "ra02"
    
    layout=1
    n_agv=2
    n_tt=0
    
    timesteps =3e5
    dynamic,size=True,(10,8)
    render_mode="solution"
    reward_f="G"
    
    agent_id=f"{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}_{reward_f}"

    samples=[]
    for _ in range (1):
        
        sample =  agent_test(
                                render_mode=render_mode,
                                benchmark=benchmark,
                                agent_id=agent_id,
                                instance=instance_id,
                                layout=layout,
                                n_agv=n_agv ,
                                n_tt=n_tt,
                                dynamic=dynamic,
                                size=size,
                                    )
        
        samples.append(sample)
        
        
    print(min(samples))
        
        

import time
import ptrl
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

#%% create environement 


def agent_test(agent_id="ra01",instance="ra01",layout=1,n_agv=2,n_tt=1,dynamic = False ,size=(None,None) ,render_mode="solution"):
    
    local_agent = f"agents/Agent_{agent_id}.zip"
    global_agent= "agents/Agent.zip"
    
    env = gym.make("ptrl-fms-v0",
                   render_mode=render_mode,
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
    
    env.seed = None
    while not terminated : 
        action_masks = get_action_masks(env)
        action, _states = model.predict(obs, action_masks=action_masks)
        obs, reward, terminated, truncated,info= env.step(action)
        i+=1 
        
    end_time = time.time()
    elapsed_time = end_time - start_time    
    env.render(n_agv=n_agv, n_tt=n_tt,job_zoom=False)
    
    
    print(f" inference took {elapsed_time} seconds") 
    print(f" Makespan : {env.sim.clock} , number of interactions {env.sim.interaction_counter}")
    # print(env.sim.delivery_history())
    return env.sim.clock

if __name__ == "__main__":

    instance_id="ra01"
    layout=2
    n_agv= 2
    n_tt= 1
    
    timesteps=3e5
    dynamic,size = False,(10,5)
    render_mode="solution"
    
    agent_id=f"{instance_id}_{layout}_{n_agv}_{n_tt}_{timesteps}"
    samples = [agent_test(agent_id,instance=instance_id,dynamic=dynamic,size=size,n_agv=n_agv ,n_tt=n_tt ,render_mode=render_mode) for _ in range(1)]
    print(min(samples),max(samples),sum(samples)/len(samples))

        
        
        
        
        

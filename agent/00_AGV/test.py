import time
import ptrl
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

#%% create environement 


def agent_test(agent_id="ta01",instance="ta01",dynamic = False ,size=(None,None) ,n_agv=0,render_mode="solution"):
    
    local_agent = f"agents/MaskablePPO-{agent_id}.zip"
    global_agent= "agents/MaskablePPO.zip"
    
    env = gym.make("ptrl-agv-v0",
                   render_mode="solution",
                   instance_id=instance_id,
                   dynamic=dynamic,
                   size=size,
                   n_agv=n_agv
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
    env.render(job_zoom=False)
    
    
        
    print(f" inference took {elapsed_time} seconds") 
    print(f" Makespan : {env.sim.clock} , number of interactions {env.sim.interaction_counter}")

    return env.sim.clock

if __name__ == "__main__":
    
    dynamic = False
    size = (10,5)
    
    n_agv= 2
    instance_id="bu01"
    time_steps=1e5
    
    
    agent_id=f"{instance_id}-{n_agv}-{time_steps}"
    
    
    samples = [agent_test(agent_id,instance=instance_id,dynamic=dynamic,size=size,n_agv=n_agv) for _ in range(1)]
    print(min(samples),max(samples),sum(samples)/len(samples))
        
        
        
        
        
        

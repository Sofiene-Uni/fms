import time
import jsspetri
import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

#%% create environement 


def agent_test(agent_id="ta01",instance="ta01",dynamic = False ,render_mode="solution"):
    
    local_agent = f"agents/MaskablePPO-{agent_id}.zip"
    global_agent= "agnets/MaskablePPO.zip"
    
    env = gym.make("jsspetri-fms-v0",
                   render_mode=render_mode,
                   instance_id=instance,
                   dynamic=dynamic
               
                
    ).unwrapped
    
    
    model = MaskablePPO.load(global_agent) if dynamic else MaskablePPO.load(local_agent)
    i,terminated,(obs,info)=0,False,env.reset()
    start_time = time.time() 
    
    env.seed = None
    
    while not terminated: 
        action_masks = get_action_masks(env)
        action, _states = model.predict(obs, action_masks=action_masks)
        obs, reward, terminated, truncated,info= env.step(action)
        

        i+=1 
        #print(i)  
        
    end_time = time.time()
    elapsed_time = end_time - start_time    
    env.render(zoom=True,rank=True,format_="pdf")
        
    print(f" inference took {elapsed_time} seconds") 
    print(f" Makespan : {env.sim.clock} , number of interactions {env.sim.interaction_counter}")

    return env.sim.clock

if __name__ == "__main__":
    
    
    instance_id="bu01"
    agent_id="bu01"

    samples = [agent_test(agent_id,instance=instance_id) for _ in range(1)]
    print(min(samples),max(samples),sum(samples)/len(samples))
        
        
        
        
        
        

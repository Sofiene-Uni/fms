import numpy as np

def get_obs(env):
    """
    Get the observation of the state.

    Returns:
        np.ndarray: Observation array.
    """
    observation = []
    
    jobs =  [p for p in env.sim.places.values() if p.uid in env.sim.filter_nodes("job")] 
    avgs =  [p for p in env.sim.places.values() if p.uid in env.sim.filter_nodes("agv_transporting")] 
    machines =  [p for p in env.sim.places.values() if p.uid in env.sim.filter_nodes("machine_processing")] 
    delivery =  [p for p in env.sim.places.values() if p.uid in env.sim.filter_nodes("delivery")]
    

    # Get the waiting operation in the jobs depending on the depth:
    for level in range(env.observation_depth):     
       for job in jobs :
           if job.token_container and level < len(job.token_container):
               observation.extend([job.color, int(job.token_container[level].time_features[0])])
           else:
               observation.extend([job.color, 0])
               
 
    #Get The state of the AGVs , ie ,remaining time : 
    for agv in avgs :     
       if not agv.token_container:
           observation.extend([agv.color,0])
       else:
           token= agv.token_container[0]
           elapsed=token.logging[list(token.logging.keys())[-1]][2]
           remaining_time =token.time_features[1] - elapsed
           observation.extend([agv.color, remaining_time if remaining_time  >=0  else 0])
        
    
    # Get the state of the machines, i.e., remaining time :
    for machine in machines :
       if not machine.token_container:
           observation.extend([machine.color,0])
       else:
           token=machine.token_container[0]
           elapsed=token.logging[list(token.logging.keys())[-1]][2]
           remaining_time =token.time_features[0] - elapsed
           observation.extend([machine.color, remaining_time if remaining_time  >=0  else 0])
 
    
    # Get the number of deliverd operation 
    observation.append(len ( delivery[0].token_container))
              
    # if dynamic fill the rest of the observation with 0   
    if env.dynamic :
        for  i in range(len(observation),env.observation_space.shape[0]):  
           observation.append(0)
                  
    return np.array(observation, dtype=np.int64)






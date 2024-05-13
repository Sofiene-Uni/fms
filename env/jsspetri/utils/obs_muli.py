import numpy as np

def get_obs(env):
    """
    Get the observation of the state.

    Returns:
        np.ndarray: Observation array.
    """
    observation = []
    # Get the state of the machines, i.e., remaining time :
    for m in range(env.sim.n_machines) :
       if len (env.sim.machines[m].token_container) == 0:
           observation.extend([env.sim.machines[m].color,0])
       else:
           in_process=env.sim.machines[m].token_container[0]
           remaining_time =in_process.process_time - in_process.logging[list(in_process.logging.keys())[-1]][2]
           observation.extend([env.sim.machines[m].color, remaining_time if remaining_time  >=0  else 0])
           
    # Get the waiting operation in the jobs depending on the depth:
    for level in range(env.observation_depth):
       for j in range(env.sim.n_jobs) :
           if env.sim.jobs[j].token_container and level < len(env.sim.jobs[j].token_container):
               observation.extend([env.sim.jobs[j].token_container[level].color[1], env.sim.jobs[j].token_container[level].process_time])
           else:
               observation.extend([0, 0])

    #Get total consumption:    
    consumption=0
    busy_machines= ~np.array( [machine.idle for machine in env.sim.machines])
    consumption =  np.dot(busy_machines , env.sim.machines_powers)
    observation.append(consumption)
 
    #Get consumption per machine:       
    for idx,machine in enumerate(env.sim.machines):
       observation.append(not machine.idle * env.sim.machines_powers[idx])
                               
    # Get the number of deliverd operation 
    for delivery in env.sim.delivery:
       observation.append(len ( delivery.token_container))
              
    # if dynamic fill the rest of the observation with -1   
    if env.dynamic :
        for  i in range(len(observation),env.observation_space.shape[0]):  
           observation.append(-1)
           
    return np.array(observation, dtype=np.int64)
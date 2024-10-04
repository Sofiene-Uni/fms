def get_obs(sim, observation_depth):
    """
    Get the observation of the state.

    Returns:
        np.ndarray: Observation array.
    """
    import numpy as np

    # Pre-filter all places into categories once to avoid repeated filtering
    sim_places = sim.places.values()
    jobs = [p for p in sim_places if p.uid in sim.filter_nodes("job")]
    agvs = [p for p in sim_places if p.uid in sim.filter_nodes("agv_transporting")]
    agvs_buffer = [p for p in sim_places if p.uid in sim.filter_nodes("agv_buffer")]
    
    tt = [p for p in sim_places if p.uid in sim.filter_nodes("tool_transporting")]
    machines = [p for p in sim_places if p.uid in sim.filter_nodes("machine_processing")]
    deliveries = [p for p in sim_places if p.uid in sim.filter_nodes("delivery")]

    observation = []
    
    # Get the operations queue
    try:
        for job in jobs:
            observation.append(len(job.token_container))

            for level in range(observation_depth):
                if job.token_container and level < len(job.token_container):
                    observation.extend([job.token_container[level].color[1], job.token_container[level].time_features[0]])
                else:
                    observation.extend([0, 0])
    except Exception as e:
        pass
        #print(f"Error in jobs loop: {e}")

    try:
        for buffer in agvs_buffer:
            if buffer.token_container:
                observation.append(len(buffer.token_container))
            else:
                observation.append(0)
    except Exception as e:
        pass
        #print(f"Error in agvs_buffer length loop: {e}")

    try:
        for buffer in agvs_buffer:
            if buffer.token_container:
                observation.append(buffer.token_container[0].color[0])
            else:
                observation.append(0)
    except Exception as e:
        pass
        #print(f"Error in agvs_buffer color loop: {e}")
    
    # Get the status of the AGV, the remaining time, and current token color
    try:
        for agv in agvs:
            if agv.token_container:
                elapsed = agv.token_container[0].logging[agv.uid][2]
                remaining_time = max(agv.token_container[0].time_features[1] - elapsed, 0)
                observation.extend([agv.token_container[0].color[1], remaining_time])
            else:
                observation.extend([0, 0])
    except Exception as e:
        pass
        #print(f"Error in agvs loop: {e}")
    
    # Get the current AGV position
    try:
        for agv in agvs:
            current_position = agv.history[-1]
            for machine in range(1, sim.n_machines + 1):
                distance = sim.instance.get_time(current_position, machine, time_type=1)
                observation.append(distance)
    except Exception as e:
        pass
        #print(f"Error in AGV position loop: {e}")
    
    # Get the state of the machines
    try:
        for machine in machines:
            if machine.token_container:
                elapsed = machine.token_container[0].logging[machine.uid][2]
                remaining_time = max(machine.token_container[0].time_features[0] - elapsed, 0)
                observation.extend([machine.token_container[0].color[1], remaining_time])
            else:
                observation.extend([0, 0])
    except Exception as e:
        pass
        #print(f"Error in machines loop: {e}")
    
    # Get the state of the tool transports
    try:
        for transporter in tt:
            if transporter.token_container:
                elapsed = transporter.token_container[0].logging[transporter.uid][2]
                remaining_time = max(transporter.token_container[0].time_features[2] - elapsed, 0)
                observation.extend([transporter.token_container[0].color[1], remaining_time])
            else:
                observation.extend([0, 0])
    except Exception as e:
        pass
        #print(f"Error in tool transports loop: {e}")
    
    # Get the number of delivered operations
    try:
        for delivery in deliveries:
            observation.append(len(delivery.token_container))
    except Exception as e:
        pass
        #print(f"Error in deliveries loop: {e}")
        
        
        
    # if dynamic fill the rest of the observation with -1   
    if sim.dynamic :
        observation_size= sim.n_jobs + 2*(sim.n_jobs*observation_depth)+ 4*sim.n_agv + (sim.n_agv*sim.n_machines)+ 2*sim.n_tt+3*sim.n_machines  
        for  i in range(len(observation),observation_size):  
           observation.append(-1)


    return np.array(observation, dtype=np.int64)




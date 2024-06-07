class Spt():
    def __init__(self):
        self.label="SPT"
        self.type_="static"
    def __str__(self):
       return  "Shortest processing time (SPT): Prioritize jobs with the initial shortest processing time."
   
    def decide(self, sim):

        def get_action_job (action):
            return sim.action_map[action][0]
     
        def get_processing_time(job):
            
            total_time=0     
            original_job = sim.instance[job]
            for op in original_job:
                total_time += op[1]
            return total_time
        
        enabled_action = [index for index, value in enumerate(sim.action_masks()) if value]  
        enabled_jobs=list (map(get_action_job,enabled_action))
        processing_times=list (map(get_processing_time,enabled_jobs))
        job=processing_times.index(min(processing_times))
        
        return  enabled_action[job]
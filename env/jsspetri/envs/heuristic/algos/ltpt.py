class Ltpt():
    def __init__(self):
        self.type_="static"
    def __str__(self):
       return  "Longest Total Processing Time (LTPT): Prioritize jobs with the least intial work  (sequence * processing_time)in the job queue."

    def decide(self, env):
        
        def get_action_job (action):
            return env.sim.action_map[action][0]
        
        def get_processing_time(job):
            total_time=0     
            original_job = env.sim.instance[job]
            for op in original_job:
                total_time += op[1]
            return total_time
                
        enabled_action = [index for index, value in enumerate(env.action_masks()) if value]  
        enabled_jobs=list (map(get_action_job,enabled_action))
        processing_times=list (map(get_processing_time,enabled_jobs))
        job=processing_times.index(min(processing_times))
        
        
        return  enabled_action[job]
class Lpt():
    def __init__(self):
        self.label = "LPT"
        self.type_ = "static"
        
    def __str__(self):
        return "Longest Processing Time (LPT): Prioritize jobs with the initial longest processing time."
   
    def decide(self, sim):
        def get_processing_time(job):
            total_time = 0
            original_job =  sim.instance[job]
            for index,(machine,process_time) in enumerate (original_job):
                total_time += process_time
    
            return total_time
        
        enabled_action = [index for index, value in enumerate(sim.action_masks()) if value]  
        enabled_jobs = [sim.action_map[action][0] for action in enabled_action]
        processing_times = [get_processing_time(job) for job in enabled_jobs]
        
        # Find the index of the job with the maximum initial processing time
        job = processing_times.index(max(processing_times))
        
        return enabled_action[job]
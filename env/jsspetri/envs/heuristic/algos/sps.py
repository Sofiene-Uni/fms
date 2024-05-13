class Sps():
    def __init__(self):
        self.label = "SPS"
        self.type_ = "static"
        
    def __str__(self):
        return "Shortest Process Sequence (SPS): Prioritize jobs with the least initial operations in the job queue."
   
    def decide(self, sim):
        def get_operation_number(job):
            original_job = sim.instance[job]
            return len(original_job)
                  
        enabled_action = [index for index, value in enumerate(sim.action_masks()) if value]  
        enabled_jobs = [sim.action_map[action][0] for action in enabled_action]
        operation_numbers = [get_operation_number(job) for job in enabled_jobs]
        
        # Find the index of the job with the minimum number of initial operations
        job = operation_numbers.index(min(operation_numbers))
        
        return enabled_action[job]
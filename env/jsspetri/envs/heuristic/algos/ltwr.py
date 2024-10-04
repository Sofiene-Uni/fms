import numpy as np

class Ltwr():
    def __init__(self):
        self.label = "LTWR"
        self.type_ = "dynamic"
        
    def __str__(self):
        return "Least Total Work remaining (LTWR): Prioritize jobs with the least total work remaining (sequence * processing times) in the job queue."
    
    def decide(self, sim):
        def get_processing_time(job):
            total_time = sum(token.process_time for token in sim.jobs[job].token_container)
            return total_time
        
        enabled_action = np.nonzero(sim.action_masks())[0]
        enabled_jobs = np.array([sim.action_map[action][0] for action in enabled_action])
        processing_times = np.array([get_processing_time(job) for job in enabled_jobs])
        
        # Find the index of the job with the minimum total work remaining
        job = np.argmin(processing_times)
        
        return enabled_action[job]
        

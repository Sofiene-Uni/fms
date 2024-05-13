import numpy as np

class Sptn():
    def __init__(self):
        self.label = "SPTX"
        self.type_ = "Dynamic"
        
    def __str__(self):
        return "Shortest Processing Time next (SPTX): Select the job with an operation that is ready to be processed next and has the shortest processing time."
   
    def decide(self, sim):
        def get_processing_time(job):
            return sim.jobs[job].token_container[0].process_time
        
        enabled_action = np.nonzero(sim.action_masks())[0]
        enabled_jobs = np.array([sim.action_map[action][0] for action in enabled_action])
        processing_times = np.array([get_processing_time(job) for job in enabled_jobs])
        
        # Find the index of the job with the minimum processing time
        job = np.argmin(processing_times)
        
        return enabled_action[job]
        
import numpy as np

class Lpsr():
    def __init__(self):
        self.label = "LPSR"
        self.type_ = "Dynamic"
        
    def __str__(self):
        return "Longest Process Sequence Remaining (LPSR): Prioritize jobs with the most operations remaining in the job queue."
   
    def decide(self, sim): 
        def get_operation_number(job):
            return len(sim.jobs[job].token_container)
                
        enabled_action = np.nonzero(sim.action_masks())[0]
        enabled_jobs = np.array([sim.action_map[action][0] for action in enabled_action])
        operation_numbers = np.array([get_operation_number(job) for job in enabled_jobs])
        
        # Find the index of the job with the maximum number of operations remaining
        job = np.argmax(operation_numbers)
        
        return enabled_action[job]
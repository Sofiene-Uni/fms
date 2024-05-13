import numpy as np

class Lwt():
    def __init__(self):
        self.label = "LWT"
        self.type_ = "dynamic"
        
    def __str__(self):
        return "Longest Waiting Time (LWT): Prioritize jobs with the highest waiting time since last allocation"

    def decide(self, sim):
        def get_waiting_time(job):
            op = sim.jobs[job].token_container[0]
            last_logging = list(op.logging.keys())[-1]
            return op.logging[last_logging][2]

        enabled_action = np.nonzero(sim.action_masks())[0]
        enabled_jobs = np.array([sim.action_map[action][0] for action in enabled_action])
        waiting_times = np.array([get_waiting_time(job) for job in enabled_jobs])
        
        # Find the index of the job with the maximum waiting time
        job = np.argmax(waiting_times)
        
        return enabled_action[job]
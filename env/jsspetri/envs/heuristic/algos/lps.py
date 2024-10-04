class Lps():
    def __init__(self):
        self.label = "LPS"
        self.type_ = "static"
        
    def __str__(self):
        return "Longest Process Sequence (LPS): Prioritize jobs with the most initial operations in the job queue."
   
    def decide(self, sim):
        def get_operation_number(job):
            original_job = sim.instance[job]
            return len(original_job)
                  
        enabled_action = [index for index, value in enumerate(sim.action_masks()) if value]  
        enabled_jobs = [sim.action_map[action][0] for action in enabled_action]
        operation_numbers = [get_operation_number(job) for job in enabled_jobs]
        
        # Find the index of the job with the maximum number of initial operations
        job = operation_numbers.index(max(operation_numbers))
        
        return enabled_action[job]
            
            
            
        
        
             
           
            

        
    
       
           
            
      
        
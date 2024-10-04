class random_gen:
    
    def __init__(self,  num_instances,
                        num_jobs,
                        num_machines,
                        num_tools, 
                       
                        machine_seed,
                        process_time_seed,
                        tools_seed,
                        
                        tools_transport_seed,
                        agv_transport_seed):
        
        self.num_instances = num_instances
        self.njobs = num_jobs
        self.nmachines = num_machines
        self.n_tools = num_tools
        
        self.machine_seed = machine_seed
        self.process_time_seed = process_time_seed
        
        self.tools_seed = tools_seed
        
        
        self.agv_transport_seeds = agv_transport_seed
        self.tools_transport_seed = tools_transport_seed
        
        
        self.processing_times = []
        self.machine_assignments = []
        self.tools_assignments = []
        
        self.avg_transport_times=[]
        self.tools_transport_times=[]
        
    def LCG(self, seed, x, y): 
        # Linear Congruential Generator (LCG)
        a = 16807
        b = 127773
        c = 2836
        m = 2**31 - 1
        
        k = seed // b
        seed = a * (seed % b) - k * c
        if seed < 0:
            seed += m  
        # Generate random number between 0 and 1
        u = seed / m
        # Save the updated seed
        return int(x + u * (y - x + 1)), seed
    
    
    def generate_transport_times(self, transport_seed, max_transport_time=30):

        transport_times = []
        for i in range(1,self.nmachines+1):
            row = []
            for j in range(1,self.nmachines+1):
                values, transport_seed = self.LCG(transport_seed, 1, max_transport_time)
                row.append(values)
            transport_times.append(row)
        
        # Set the diagonal elements to zero same machine
        for i in range(1,self.nmachines+1):
            transport_times[i-1][i-1] = 0
        
        return transport_times
    
    
    def generate_processing_times(self,max_process_time=99):
 
        processing_times = []
        for i in range(1,self.njobs+1):
            row = []
            for j in range(1,self.nmachines+1):
                values, self.process_time_seed = self.LCG(self.process_time_seed, 1, max_process_time)
                row.append(values)
            processing_times.append(row)
        return processing_times
    
    
    def generate_resource_assignments(self, resource_seed, n_resource):
        resource_assignments = []
        for i in range(1,self.njobs+1):
            row = list(range(1, n_resource+1)) 
            for j in range(1, n_resource+1):
                swap_index, resource_seed = self.LCG(resource_seed, j, n_resource)
                row[j - 1], row[swap_index - 1] = row[swap_index - 1], row[j - 1]  
            resource_assignments.append(row)
        return resource_assignments
    
    
    def get_values(self):
        
        for i in range(1,self.num_instances+1): 
            self.processing_times.append(self.generate_processing_times())
            self.machine_assignments.append(self.generate_resource_assignments(self.machine_seed, self.nmachines))   
            self.tools_assignments.append(self.generate_resource_assignments(self.tools_seed, self.n_tools))
            
        self.avg_transport_times=self.generate_transport_times(self.agv_transport_seeds,max_transport_time=30)
        self.tools_transport_times=self.generate_transport_times(self.tools_transport_seed,max_transport_time=30)
                  
        return self.processing_times, self.machine_assignments, self.tools_assignments , self.tools_transport_times ,self.avg_transport_times


if __name__=="__main__":
    
    num_instances=2
    num_jobs = 15
    num_machines = 15
    num_tools= 15 
    
    tools_seed = 170719940
    machine_seed = 398197754
    process_time_seed = 840612802
    
    tools_transport_seed = 280219920
    agv_transport_seed = 180119550
    
    
    instance_generator = random_gen( num_instances,
                                     num_jobs,
                                     num_machines,
                                     num_tools, 
                                    
                                     machine_seed,
                                     process_time_seed,
                                     tools_seed,
                                     
                                     tools_transport_seed,
                                     agv_transport_seed,)
        
        
    processing_times,machine_assignments,tools_assignments,tools_transport_times,avg_transport_times=instance_generator.get_values()


    for i in range (1,len(processing_times)+1):
        
        print("Processing Times:")
        for row in processing_times[i-1]:
            print(row)   
            
        print("\nMachine Assignments:")
        for row in machine_assignments[i-1]:
            print(row)
            
        print("\ntools Assignments:")
        for row in tools_assignments[i-1]:
            print(row)
            
        print("\ntools transport times:")
        for row in tools_transport_times:
            print(row)
            
        print("\n agv transport times:")
        for row in avg_transport_times:
            print(row)


    
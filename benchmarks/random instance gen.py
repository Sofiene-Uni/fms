import os 
import pandas as pd 
from LCG_generator import random_gen 

class Instance_gen:
    
    def __init__(self,num_instances,
                      num_jobs,
                      num_machines,
                      num_tools, 
                       
                      machine_seed,
                      process_time_seed,
                      tools_seed,
                        
                      tools_transport_seed,
                      agv_transport_seed):


        instance_generator = random_gen(  num_instances,
                                          num_jobs,
                                          num_machines,
                                          num_tools, 
                                           
                                          machine_seed,
                                          process_time_seed,
                                          tools_seed,
                                            
                                          tools_transport_seed,
                                          agv_transport_seed)


        self.njob = num_jobs
        self.nmachine = num_machines
        self.ntools = num_tools
        
        self.processing_times, self.machine_assignments, self.tools_assignments , self.tools_transport_times ,self.avg_transport_times = instance_generator.get_values()
        
        
    
    def zip_inputs(self):
        instances_list = []
        for time, machine,tool in zip(self.processing_times, self.machine_assignments,self.tools_assignments):
            instance_temp = []
            for job_time, job_machine ,tool in zip(time, machine ,tool):
                instance_temp.append([value for triplet in zip(job_machine,tool,job_time) for value in triplet])
            instances_list.append(pd.DataFrame(instance_temp))
        return instances_list
    
    
    def display(self): 
        for i in range(len(self.processing_times)):
            print("Processing Times:")
            for row in self.processing_times[i]:
                print(row)
            print("\nMachine Assignments:")
            for row in self.machine_assignments[i]:
                print(row)
            print("\nTools Assignments:")
            for row in self.tools_assignments[i]:
                print(row)
    
    def export_instances(self): 
        dict_ = {
            (15, 15,15): "sl0", (20, 15,15): "sl1", (20, 20,20): "sl2", (30, 15,15): "sl3",
            (30, 20,20): "sl4", (50, 15,15): "sl5", (50, 20, 20): "sl6", (100, 20 ,20): "sl7",
        }
        
        folder_name = "random_instances"
        instance_path = os.path.join(os.path.dirname(__file__), folder_name)
        
        # Check if the folder exists, create it if it doesn't
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        # Loop through instances and write them to files
        for idx, instance in enumerate(self.zip_inputs()):
            file_name = f"{dict_[(self.njob,self.nmachine,self.ntools)]}{idx}"
            instance_str = f"{self.njob} {self.nmachine} {self.ntools}" + '\n' + instance.to_string(index=False, header=False)
            with open(os.path.join(instance_path, file_name), "w") as file:
                file.write(instance_str)
                
                
                
    def export_transport_times(self,nmachine,layout=1): 
         
         folder_name = "random_instances"
         instance_path = os.path.join(os.path.dirname(__file__), folder_name)
         
         # Check if the folder exists, create it if it doesn't
         if not os.path.exists(instance_path):
             os.makedirs(instance_path)
             
         agv_file_name = f"trans_{nmachine}_{layout}"
         times_df= pd.DataFrame(self.avg_transport_times)
         agv_times_matrix_str= times_df.to_string(index=False, header=False)
         with open(os.path.join(instance_path,  agv_file_name), "w") as file:
             file.write( agv_times_matrix_str)
             
             
         tt_file_name = f"tt_{nmachine}_{layout}"
         tt_times_df= pd.DataFrame(self.tools_transport_times)
         tt_times_matrix_str=tt_times_df.to_string(index=False, header=False)
         
         with open(os.path.join(instance_path, tt_file_name), "w") as file:
            file.write(tt_times_matrix_str )
         
                


if __name__ == "__main__":
    
    num_instances = 1


    machine_seed = 398197754
    process_time_seed = 840612802
    tools_seed = 170719940
    
    tools_transport_seed = 280219920
    agv_transport_seed = 180119550
    
    instance_sizes = [(15, 15,15), (20, 15,15), (20, 20,20), (30, 15,15), (30, 20,20), (50, 15,15), (50, 20, 20), (100, 20 ,20)]

    for num_jobs, num_machines,num_tools in instance_sizes:
        
        inst_gen = Instance_gen(num_instances,
                                num_jobs,
                                num_machines,
                                num_tools, 
                           
                                machine_seed,
                                process_time_seed,
                                tools_seed,
                            
                                tools_transport_seed,
                                agv_transport_seed)

        instances = inst_gen.export_instances()
        
        inst_gen.export_transport_times(num_machines,layout=1)
        

    

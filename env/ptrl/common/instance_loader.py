import os
import pandas as pd


class InstanceLoader:
    
    def __init__(self, benchmark="Taillard", instance_id=None ,layout=1):
        
        self.benchmark = self.validate_benchmark(benchmark)
        self.layout=layout
        
        if instance_id is None:
            raise ValueError("An instance_id must be provided.")
        
        self.instance_id = instance_id
        self.job_sequences, self.specs = self.load_instance(instance_id)
        self.n_jobs, self.n_machines, self.n_tools, self.max_bound = self.specs
        self.agv_times = self.load_agv_durations(self)
        self.tt_times = self.load_tt_durations(self)
        
    def validate_benchmark(self, benchmark):
        valid_benchmarks = ["Taillard", "BU", "Demirkol", "Raj"]
        if benchmark not in valid_benchmarks:
            raise ValueError(f"Benchmark must be one of: {', '.join(valid_benchmarks)}")
        return benchmark
        
    def load_instance(self, instance_id):
        instance_path = os.path.join(os.path.dirname(__file__), 'instances', self.benchmark, instance_id)
        data = []

        try:
            with open(instance_path, 'r') as file:
                for line in file:
                    elements = line.strip().split()
                    data.append(elements)
                print(f"{self.benchmark} Instance '{instance_id}' is loaded.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None, []

        instance_raw = pd.DataFrame(data)
        specs = list(instance_raw.iloc[0].dropna().astype(int))
        instance_raw = instance_raw.drop(0).apply(pd.to_numeric, errors='coerce')
        specs.append(instance_raw.max().max())  # Add the max bound

        n_features = len(specs) - 1
        instance = []

        for _, row in instance_raw.iterrows():
            job = []
            for i in range(0, len(row) - (n_features - 1), n_features):
                if not any(pd.isna(val) for val in row[i:i + n_features]):
                    job.append(tuple(row[i:i + n_features].astype(int)))
            instance.append(job)

        return instance, specs
    
    def load_agv_durations(self, layout=1):
        instance_path = os.path.join(os.path.dirname(__file__), 'instances', self.benchmark, f"trans_{self.n_machines}_{self.layout}")
        data = []

        try:
            with open(instance_path, 'r') as file:
                for line in file:
                    elements = line.strip().split()
                    data.append(elements)
        except FileNotFoundError:
            print(f"The file '{instance_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

        return pd.DataFrame(data)
    
    def load_tt_durations(self, layout=1):
        instance_path = os.path.join(os.path.dirname(__file__), 'instances', self.benchmark, f"tt_{self.n_machines}_{self.layout}")
        data = []

        try:
            with open(instance_path, 'r') as file:
                for line in file:
                    elements = line.strip().split()
                    data.append(elements)
        except FileNotFoundError:
            print(f"The file '{instance_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

        return pd.DataFrame(data)
    

    def get_time(self,origin, destination ,time_type=1 ):
        
        trans_time = 0
        
        if time_type==2:       
                time_matrix=self.tt_times
        else :      
            time_matrix=self.agv_times
            
        if origin is None:  # Load operation
            trans_time = int(time_matrix.iloc[0][destination + 1])
        elif destination is None:  # Unload operation
            trans_time = int(time_matrix.iloc[origin + 1][0])
        elif origin != destination:  # Change of machine operation
            trans_time = int(time_matrix.iloc[origin + 1][destination + 1])
            
        return trans_time



# %% Test
if __name__ == "__main__":
    
    
     #benchmarks : "Taillard", "BU", "Demirkol"
     benchmark="Raj"
     instance_id= "ra01"
     layout=1
     
     instance =InstanceLoader(benchmark=benchmark,instance_id=instance_id,layout=layout)
     

     
     
     
     
     
   
    





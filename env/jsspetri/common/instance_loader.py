import os
import pandas as pd

def load_instance_raw(instance_id,benchmark):
    """
    Load raw instance data from a file.

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        pandas.DataFrame: The raw instance data.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
               
    instance_path = f"{os.path.dirname(__file__)}\\instances\\{benchmark}\\{instance_id}"
    data = []
    job_lens = []
    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
                job_lens.append(len(elements))
           # print(f"Instance '{instance_id}' is loaded.")
    except FileNotFoundError:
        print(f"The file '{instance_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    dummy_machines = 0
    for task in data[1:]:
        while len(task) != max(job_lens):
            is_variable = True
            dummy_machines = 1
            task.extend([0,-1])
    raw_instance = pd.DataFrame(data)
    n_job, n_machine = tuple(raw_instance.iloc[0].dropna().astype(int))
    n_machine += dummy_machines
    n_features = int((raw_instance.shape[1] - (n_machine * 2)) / n_machine) + 1
    raw_instance = raw_instance.drop(0).apply(pd.to_numeric, errors='coerce')
    raw_instance.fillna(0, inplace=True)
    
    max_bound=raw_instance.max().max()
    return raw_instance, (n_job, n_machine, n_features,max_bound, is_variable)

def load_instance(instance_id,benchmark="Taillard"):
    

    """
    Load instance data from a file and organize it into a structured format.

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        list: A list containing dictionaries representing the operation sequence for each job.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    
    if benchmark not in ["Taillard", "Taillard_random", "Demirkol", "BU", "Raj"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'Taillard_random', 'Demirkol', 'BU', 'Raj'")
    
    raw_instance, (n_job, n_machine, n_features ,max_bound, is_variable) = load_instance_raw(instance_id,benchmark)
    instance = []
    for job_index in range(raw_instance.shape[0]):   
        job = {}
        for op_index in range(0, raw_instance.shape[1], n_features + 1):
            key = raw_instance.iloc[job_index, op_index]
            values = list(raw_instance.iloc[job_index, op_index + 1: op_index + n_features + 1]) 
            job[key] = values      
        instance.append(job)
           
    return instance, (n_job, n_machine, n_features ,max_bound, is_variable)



def load_trans(n_machine,benchmark="Taillard", trans_layout = None, is_variable = False):
    

    """
    Load transport time  data from a file .

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        list: A list containing dictionaries representing the operation sequence for each job.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    
    if benchmark not in ["Taillard", "Taillard_random", "Demirkol","BU","Raj"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'Taillard_random', 'Demirkol', 'BU', 'Raj'")

    if trans_layout is not None and trans_layout != '':
        instance_path = f"{os.path.dirname(__file__)}\\instances\\{benchmark}\\{trans_layout}"
    else:
        instance_path = f"{os.path.dirname(__file__)}\\instances\\{benchmark}\\trans_{n_machine}"
    trans_matrix=None
    
    data=[]
    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
                if is_variable:
                    elements.insert(0, 0)
        if is_variable:
            data.append([0 for i in range(len(data[0]))])
          
    except FileNotFoundError:
        print(f"The file '{instance_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    trans_matrix = pd.DataFrame(data)   

    
   
    return trans_matrix

# %% Test
if __name__ == "__main__":
    
     instance_id= "ta01"
     instance,size = load_instance(instance_id)
     n_job, n_machine, n_features ,max_bound=size

     print (load_trans(n_machine))
     
     
     
     
     
     
     
   
    





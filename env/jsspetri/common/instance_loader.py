import os
import pandas as pd



def load_instance(instance_id,benchmark="Taillard"):
    

    """
    Load instance data from a file and organize it into a structured format.

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        list: A list containing dictionaries representing the operation sequence for each job.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    
    if benchmark not in ["Taillard", "BU", "Demirkol"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'Taillard_random', 'Demirkol'")
    
    instance_path = f"{os.path.dirname(__file__)}\\instances\\{benchmark}\\{instance_id}"
    data = []
    

    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
            print(f" {benchmark} Instance '{instance_id}' is loaded.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    instance_raw = pd.DataFrame(data)
    
    n_job, n_machine = tuple(instance_raw.iloc[0].dropna().astype(int))
    instance_raw = instance_raw.drop(0).apply(pd.to_numeric, errors='coerce')
    
    max_bound=instance_raw.max().max()
    
    
    instance=[]
    for index, row in instance_raw.iterrows():
        job=[]
        for i in range(0, len(row)-1, 2):
            if not pd.isna(row[i]) and not pd.isna(row[i+1]):
                job.append((int (row[i]), row[i+1])) 
                
        instance.append(job)

    return instance, (n_job, n_machine, max_bound)



def load_trans(n_machine,layout=1,benchmark="Taillard"):
    

    """
    Load transport time  data from a file .

    Parameters:
        instance_id (str): The identifier of the instance to load.

    Returns:
        list: A list containing dictionaries representing the operation sequence for each job.
        tuple: A tuple containing the number of jobs, number of machines, and number of features.
    """
    
    if benchmark not in ["Taillard", "BU", "Demirkol"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'Taillard_random', 'Demirkol'")
        
    instance_path = f"{os.path.dirname(__file__)}\\instances\\{benchmark}\\trans_{n_machine}_{layout}"
    trans_matrix=None
    
    data=[]
    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
          
    except FileNotFoundError:
        print(f"The file '{instance_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    trans_matrix = pd.DataFrame(data)   
    
    return trans_matrix

# %% Test
if __name__ == "__main__":
    
    
     #benchmarks : "Taillard", "BU", "Demirkol"
    
    
     benchmark="BU"
     instance_id= "bu01"
     
     instance,size = load_instance(instance_id,benchmark="BU")
     n_job, n_machine,max_bound=size
     

     
                 
         

  

     
     
     
     
     
     
     
   
    





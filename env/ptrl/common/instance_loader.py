import os
import pandas as pd

def load_instance(instance_id, benchmark="Taillard"):
    """
    Load instance data from a file and organize it into a structured format.

    Parameters:
    ----------
    instance_id : str
        The identifier of the instance to load.
    benchmark : str, optional
        Specifies the benchmark dataset to load. Must be one of: 'Taillard', 'BU', 'Demirkol', 'Raj'.

    Returns:
    -------
    instance : list
        A list containing job information structured as a list of tuples.
    specs : list
        A list of integers representing instance specifications.

    """
    
    if benchmark not in ["Taillard", "BU", "Demirkol", "Raj"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'BU', 'Demirkol', 'Raj'")
    
    instance_path = os.path.join(os.path.dirname(__file__), 'instances', benchmark, instance_id)
    data = []

    try:
        with open(instance_path, 'r') as file:
            for line in file:
                elements = line.strip().split()
                data.append(elements)
            print(f"{benchmark} Instance '{instance_id}' is loaded.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
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


def load_trans(n_machine, layout=1, benchmark="Taillard"):
    """
    Load transport time data from a file.

    Parameters:
    -----------
    n_machine : int
        Number of machines for which transport time data is loaded.
    layout : int, optional
        Layout identifier (default is 1).
    benchmark : str, optional
        Specifies the benchmark dataset to load. Must be one of: 'Taillard', 'BU', 'Demirkol', 'Raj'.

    Returns:
    --------
    trans_matrix : pd.DataFrame or None
        DataFrame containing transport time data if successfully loaded, else None.

    """
    
    if benchmark not in ["Taillard", "BU", "Demirkol", "Raj"]:
        raise ValueError("Benchmark must be one of: 'Taillard', 'BU', 'Demirkol', 'Raj'")
        
    instance_path = os.path.join(os.path.dirname(__file__), 'instances', benchmark, f"trans_{n_machine}_{layout}")
    trans_matrix = None
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
        
    trans_matrix = pd.DataFrame(data)   
    
    return trans_matrix

# %% Test
if __name__ == "__main__":
    
    
     #benchmarks : "Taillard", "BU", "Demirkol"
     benchmark="Raj"
     instance_id= "ra01"
     
     instance,specs = load_instance(instance_id,benchmark=benchmark)

     print(instance)
     print(specs)
     

     
 
     
     
     
     
     
     
     
   
    





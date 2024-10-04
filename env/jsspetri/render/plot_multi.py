import os
import numpy as np 
from datetime import datetime
import matplotlib.cm as cm
import matplotlib.pyplot as plt


def plot_solution(jssp ,mix ,format_="jpg" ,dpi=300 ,show_rank=False): 
    
    renders_folder = f"{os.getcwd()}\\renders\\"
    if not os.path.exists(renders_folder):
        os.makedirs(renders_folder)
        
    solution_folder=  renders_folder + str(jssp.instance_id)
    if not os.path.exists(solution_folder):
        os.makedirs(solution_folder)   
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_path = f"{solution_folder}/{current_datetime}.jpg"
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)  

           
    data_dict = {
         "machine_names": [],
         "token_rank": [],
         "entry_values": [],
         "process_times": [],
         "jobs": []
     }
     
    finished_tokens = jssp.delivery_history[list(jssp.delivery_history.keys())[-1]]
    for token in finished_tokens:
        for machine, entry in token.logging.items():
            if machine in jssp.filter_nodes("machine"):
                
                data_dict["machine_names"].append(f"M {jssp.places[machine].color}")
                data_dict["token_rank"].append(token.order)
                data_dict["entry_values"].append(entry[0])
                data_dict["process_times"].append(entry[2])
                data_dict["jobs"].append(token.color[0])
                  
    unique_jobs = list(set(data_dict["jobs"]))
    color_map = plt.cm.get_cmap("tab20", len(unique_jobs))
    job_color_mapping = {job_number: color_map(i) for i, job_number in enumerate(unique_jobs)}
    colors = [job_color_mapping[job_number] for job_number in data_dict["jobs"]]
    
    
   

    # Create the first bar plot with transparency
    bars=ax1.barh(
                    y=data_dict["machine_names"],
                    left=data_dict["entry_values"],
                    width=data_dict["process_times"],
                    height=0.5,
                    color=colors,
                    alpha=1  # Set transparency to 50%
                )

    ax1.set_ylabel('Machine id')
    ax1.set_title(f"{jssp.instance_id}  :{jssp.n_jobs} X {jssp.n_machines} , Objectif Mix : {mix[0]*100}% Utilization {mix[1]*100}% Energy", fontsize=18, fontweight='bold')

    # Print token ranks on top of the bars if show_rank is True
    if show_rank:
        for bar, rank in zip(bars, data_dict["token_rank"]):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                    f'{rank}', ha='center', va='center', color='black', fontsize=8)

 
    average_consumption=np.array(jssp.energy_consumption).mean()
    energy_utils=average_consumption/jssp.max_consumption
    
    machines_util=(jssp.machines_busy.mean()/jssp.clock)
    
    x_values = np.arange(0, jssp.clock) 
    target_values = np.full_like(x_values,jssp.target_consumption)
    min_values= np.full_like(x_values, jssp.min_consumption)
    max_values= np.full_like(x_values, jssp.max_consumption)
   
    ax2.plot(x_values, max_values, color='red', linewidth=2)
    ax2.plot(x_values, target_values, color='green', linewidth=2) 
    ax2.plot(x_values, min_values, color='red', linewidth=2) 
    
    ax2.plot(jssp.interaction_timing, jssp.energy_consumption, color='blue', linewidth=1) 
    ax2.set_ylabel('Energy Consumption (Power unit)')
    ax2.set_xlabel(f"C_max  ({jssp.clock} steps) , machines util: {np.round(machines_util*100,2)} %  Energy util :{np.round(energy_utils*100,2)} %" ,fontsize=16)

    plt.tight_layout()  
    plt.show() 
    
    fig.savefig(file_path, format_=format_, dpi=dpi)

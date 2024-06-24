import os
import numpy as np 
from datetime import datetime
import matplotlib.cm as cm
import matplotlib.pyplot as plt


    
def plot_solution(jssp, show_rank=False, format_="jpg", dpi=300):
    renders_folder = f"{os.getcwd()}\\renders\\"
    if not os.path.exists(renders_folder):
        os.makedirs(renders_folder)
        
    solution_folder = renders_folder + str(jssp.instance_id)
    if not os.path.exists(solution_folder):
        os.makedirs(solution_folder)
        
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_path = f"{solution_folder}/{current_datetime}.{format_}"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)  

    # Data for the AGV plot
    agv_data_dict = {
        "agv_id": [],
        "token_rank": [],
        "entry_values": [],
        "process_times": [],
        "token_role": [],
        "jobs": []
    }
    
    
    jssp_data_dict = {
        "machine_names": [],
        "token_rank": [],
        "entry_values": [],
        "process_times": [],
        "jobs": []
    }

    finished_tokens = jssp.delivery_history[list(jssp.delivery_history.keys())[-1]]
    for token in finished_tokens:
        for place, entry in token.logging.items():
            if place in jssp.filter_nodes("agv_transporting"):
                agv_data_dict["agv_id"].append(f"AGV- {jssp.places[place].color}")
                agv_data_dict["token_rank"].append(token.order)
                agv_data_dict["token_role"].append(token.role)
                agv_data_dict["entry_values"].append(entry[0])
                agv_data_dict["process_times"].append(entry[2])
                agv_data_dict["jobs"].append(token.color[0])
                
 
            if place in jssp.filter_nodes("machine_processing"):
                jssp_data_dict["machine_names"].append(f"M {jssp.places[place].color}")
                jssp_data_dict["token_rank"].append(token.order)
                jssp_data_dict["entry_values"].append(entry[0])
                jssp_data_dict["process_times"].append(entry[2])
                jssp_data_dict["jobs"].append(token.color[0])
                
    unique_jobs = list(set(agv_data_dict["jobs"]))
    color_map = plt.cm.get_cmap("tab20b", len(unique_jobs))
    job_color_mapping = {job_number: color_map(i) for i, job_number in enumerate(unique_jobs)}
    agv_colors = [job_color_mapping[job_number] for job_number in agv_data_dict["jobs"]]
    jssp_colors = [job_color_mapping[job_number] for job_number in jssp_data_dict["jobs"]]
    
    jssp_bars = ax1.barh(
        y=jssp_data_dict["machine_names"],
        left=jssp_data_dict["entry_values"],
        width=jssp_data_dict["process_times"],
        height=0.5,
        color=jssp_colors
    )

   
    for bar, rank in zip(jssp_bars, jssp_data_dict["token_rank"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                f'{rank}', ha='center', va='center', color='black', fontsize=16)
             
    agv_bars = ax2.barh(
        y=agv_data_dict["agv_id"],
        left=agv_data_dict["entry_values"],
        width=agv_data_dict["process_times"],
        height=0.5,
        color=agv_colors
    )
    
    for bar, rank, role in zip(agv_bars, agv_data_dict["token_rank"], agv_data_dict["token_role"]):
        
        if rank == 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                    'L', ha='center', va='center', color='black', fontsize=16)
            
        elif role == "op":
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                    f'{rank}', ha='center', va='center', color='black', fontsize=16)
            
        elif token.role == "u": 
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                      "U", ha='center', va='center', color='black', fontsize=16)
            
     
            
            

    ax2.tick_params(axis='x', labelsize=16)
    ax1.tick_params(axis='y', labelsize=16)
    ax2.tick_params(axis='y', labelsize=16)
    ax1.grid(axis='x')
    ax2.grid(axis='x')
    
    ax1.set_title(f"AGVs Schedule for instance {jssp.instance_id}  : {jssp.n_jobs} jobs, {jssp.n_machines} machines, {jssp.n_agv} AGV", fontsize=18, fontweight='bold')
    ax2.set_xlabel(f"Makespan :{jssp.clock} steps" ,fontsize=16)
    
    
    # Create a legend for job numbers and colors below the x-axis with stacked elements
    legend_labels = {job_number: color_map(i) for i, job_number in enumerate(unique_jobs)}
    legend_patches = [plt.Line2D([0], [0], color=color, lw=5, label=str(job_number)) for job_number, color in legend_labels.items()]
    legend = ax2.legend(handles=legend_patches, title='Job_id', title_fontsize=16, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=10, handlelength=1)
    
    for text in legend.get_texts():
        text.set_fontsize(16)
  
    plt.tight_layout()  
    plt.show() 
    fig.savefig(file_path, format=format_, dpi=dpi)
    

def plot_job(jssp,job=0 ,format_="jpg" ,dpi=300 ,n_agv=0): 
    renders_folder = f"{os.getcwd()}\\renders\\"
    if not os.path.exists(renders_folder):
        os.makedirs(renders_folder)
        
    solution_folder=  renders_folder + str(jssp.instance_id)
    if not os.path.exists(solution_folder):
        os.makedirs(solution_folder)
        
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_path = f"{solution_folder}/{current_datetime}.jpg"

    #the tokens in the delivery places at the last time step :
    finished_tokens = jssp.delivery_history[list(jssp.delivery_history.keys())[-1]] 
    
    operations_list =[]
    
    for token in   finished_tokens :
        if token.color[0] == job:
            operations_list.append(token)

    transport_dict = {
        "operation":[],
        "entry_values": [],
        "duration": [],
        }        
 
    buffer_dict = {
        "operation":[],
        "entry_values": [],
        "duration": [],
        }
    
    
    machine_dict = {
        "operation":[],
        "machine":[],
        "entry_values": [],
        "duration": [],
        
        }
    
    job_makespan=0
    for token in  operations_list :
            for place, entry in token.logging.items():
                if place in jssp.filter_nodes("machine"): 
                    
                    machine_dict["operation"].append(token.order)
                    machine_dict["machine"].append(token.color[1])
                    machine_dict["entry_values"].append(entry[0])
                    machine_dict["duration"].append(entry[2])
                    
                    if  entry[0]+entry[2]>job_makespan:
                        job_makespan=entry[0]+entry[2]
                        
                        
                elif place in jssp.filter_nodes("agv"):
                     transport_dict["operation"].append(token.order)
                     transport_dict["entry_values"].append(entry[0])
                     transport_dict["duration"].append(token.trans_time)
                        
                        
                elif place in jssp.filter_nodes("ready"):
                    buffer_dict["operation"].append(token.order)
                    buffer_dict["entry_values"].append(entry[0])
                    buffer_dict["duration"].append(entry[2])
                    

    unique_machines = list(set(machine_dict["machine"]))
    color_map = plt.cm.get_cmap("tab20b", len(unique_machines))

    machine_color_mapping = {machine_number: color_map(i) for i, machine_number in enumerate( unique_machines)}
    colors = [machine_color_mapping[machine_number] for machine_number in machine_dict["machine"]]              
                    
    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.grid(False)

    ax.barh(
    y=transport_dict["operation"],
    left=transport_dict["entry_values"],
    width=transport_dict["duration"],
    height=0.6,
    color=["red"] * len(transport_dict["operation"]))

    ax.barh(
    y=buffer_dict["operation"],
    left=buffer_dict["entry_values"],
    width=buffer_dict["duration"],
    height=0.6,
    color=["black"] * len(buffer_dict["operation"]))
    
    bars=ax.barh(
    y=machine_dict["operation"],
    left=machine_dict["entry_values"],
    width=machine_dict["duration"],
    height=0.7,
    color=colors) 
    for bar, rank in zip(bars, machine_dict["machine"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                f'{rank}', ha='center', va='center', color='black', fontsize=12)


    # Create a legend for machines numbers and colors below the x-axis with stacked elements
    legend_labels = {machine_number: color_map(i) for i, machine_number in enumerate(unique_machines)}
    legend_patches = [plt.Line2D([0], [0], color=color, lw=4, label=str(machine_number)) for machine_number, color in legend_labels.items()]
    legend = ax.legend(handles=legend_patches, title='Machine_id', title_fontsize=16, loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=10, handlelength=1)
    
    legend_labels = {'Waiting in machine buffer': 'black', 'AGV Transport Time': 'red'}
    legend_patches = [plt.Line2D([0], [0], color=color, lw=4, label=label) for label, color in legend_labels.items()]
    
    legend2 = ax.legend(handles=legend_patches, title='Legend', title_fontsize=16, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, handlelength=2)
    ax.add_artist(legend)
    
    # Set the fontsize of legend items
    for text in legend.get_texts() + legend2.get_texts() :
        text.set_fontsize(14)  
        
    # Adjust the fontsize of the x and y axis labels
    ax.tick_params(axis='x', labelsize=16) 
    ax.tick_params(axis='y', labelsize=16) 
    ax.set_title(f" JSSP : {jssp.instance_id}: {jssp.n_jobs}X {jssp.n_machines} , Job : {job} sheduling details", fontsize=18, fontweight='bold')

    ax.set_xlabel(f"Job Makespan :{job_makespan} steps" ,fontsize=16)
    ax.set_ylabel("Operation number" ,fontsize=16)
   
    plt.tight_layout()  
    plt.show() 
    #fig.savefig(file_path, format_=format_, dpi=dpi)
    
                


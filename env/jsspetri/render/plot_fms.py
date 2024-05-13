import os
import numpy as np 
from datetime import datetime
import matplotlib.cm as cm
import matplotlib.pyplot as plt


def plot_solution(jssp, show_rank=False ,format_="jpg" ,dpi=300): 
    
    renders_folder = f"{os.getcwd()}\\renders\\"
    if not os.path.exists(renders_folder):
        os.makedirs(renders_folder)
        
    solution_folder=  renders_folder + str(jssp.instance_id)
    if not os.path.exists(solution_folder):
        os.makedirs(solution_folder)
        
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_path = f"{solution_folder}/{current_datetime}.jpg"

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

    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.grid(False)
    bars = ax.barh(
        y=data_dict["machine_names"],
        left=data_dict["entry_values"],
        width=data_dict["process_times"],
        height=0.5,
        color=colors
    )

    ax.set_xlabel(f"Makespan :{jssp.clock} steps" ,fontsize=16)
   
    # Print token ranks on top of the bars if show_rank is True
    if show_rank:
        for bar, rank in zip(bars, data_dict["token_rank"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, 
                    f'{rank}', ha='center', va='center', color='black', fontsize=8)

    # Create a legend for job numbers and colors below the x-axis with stacked elements
    legend_labels = {job_number: color_map(i) for i, job_number in enumerate(unique_jobs)}
    legend_patches = [plt.Line2D([0], [0], color=color, lw=4, label=str(job_number)) for job_number, color in legend_labels.items()]
    legend = ax.legend(handles=legend_patches, title='Job Number', title_fontsize=16, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=10, handlelength=1)
    
    # Set the fontsize of legend items
    for text in legend.get_texts():
        text.set_fontsize(14)  

    # Adjust the fontsize of the x and y axis labels
    ax.tick_params(axis='x', labelsize=16) 
    ax.tick_params(axis='y', labelsize=16) 
    ax.set_title(f"Jssp Solution Visualization for {jssp.instance_id}  : {jssp.n_jobs} jobs X {jssp.n_machines} machines", fontsize=18, fontweight='bold')


    plt.tight_layout()  
    plt.show() 
    fig.savefig(file_path, format_=format_, dpi=dpi)
    
    
    

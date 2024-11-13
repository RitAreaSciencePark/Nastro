#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import json

# Function to load JSON data from a file
def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
        return data

def create_sbatch_file(path_to_config, path_to_sbatch):
    '''
    Function to create a Slurm sbatch script based on a configuration
    file (config.json). See the documentation to understand what each 
    parameter represents
    '''
    # Get the number of nodes that will be used for the basecalling
    data = load_json(path_to_config)

    # Open the sbatch file for writing
    with open(path_to_sbatch, "w") as sbatch_file:
        # Write the basic sbatch directives
        sbatch_file.write('#!/bin/bash\n')
        sbatch_file.write(f"#SBATCH --job-name=AL-{data['General']['name']}\n")
        sbatch_file.write(f"#SBATCH --time={data['General']['run_time']}\n")
        sbatch_file.write(f"#SBATCH --output={data['Slurm']['output_path']}\n")
        sbatch_file.write(f"#SBATCH --error={data['Slurm']['error_path']}\n")
        
        sbatch_file.write(f"#SBATCH -A lage -p {data['ComputingResources']['node_queue']}")
        # If a specific node is not specified let slurm decide
        if data['ComputingResources']['node_name'] != "":
            sbatch_file.write(f" --nodelist={data['ComputingResources']['node_name']}")
        sbatch_file.write(f" --nodes=1 --ntasks-per-node=1")
        sbatch_file.write(f" --cpus-per-task={data['ComputingResources']['node_cpus']}")
        sbatch_file.write(f" --mem={data['ComputingResources']['node_mem']}")
        sbatch_file.write("\n")

        # Use the resource profiler
        sbatch_file.write("python3 ${HOME}/Nastro/GPU_log/resource_profiling.py $SLURM_MEM_PER_NODE $SLURM_CPUS_ON_NODE /orfeo/cephfs/home/area/jenkins_onpexp/Nastro.csv AL &\n")
        sbatch_file.write("profiling_pid=$!\n")

        # Write additional sbatch directives for script execution
        sbatch_file.write('config=$1\n')
        sbatch_file.write('id=$2\n')
        sbatch_file.write('samplesheet=$3\n')
        sbatch_file.write("\n")

        sbatch_file.write(f"{data['Slurm']['main_script']} $config $id $samplesheet\n")
        sbatch_file.write("kill $profiling_pid\n")

        # Add a comment indicating the script was generated by configuration.py
        sbatch_file.write('#**********WRITTEN BY CONFIGURATION.PY**********\n')
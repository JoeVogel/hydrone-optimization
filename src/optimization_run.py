import json
import pandas as pd
import time
import os
import csv

from datetime import datetime
from evolutionary_strategy import Solver, EvolutionaryStrategy

all_valid_solutions = {
                        "V_S":[],
                        "Z":[],
                        "D":[],
                        "AEdAO":[],
                        "PdD":[],
                        "P_B":[],
                        "Strength":[],
                        "Strength_Min":[],
                        "Cavitation":[],
                        "Cavitation_Max":[],
                        "Tip_Velocity":[],
                        "Tip_Velocity_Max":[],
                        "Generation":[],
                        "Run":[]
                    }

def get_best(file_path):
    df = pd.read_csv(file_path) 
    
    df['Valid'] = df['Valid'].astype(bool)
    
    df_valid = df[df['Valid'] == True]
    
    has_valids = False
    
    if (len(df_valid.index) > 0):
        min_pb_row = df_valid.loc[df_valid['P_B'].idxmin()]
    
        has_valids = True
    
        return has_valids, min_pb_row
    
    return has_valids

def save_run_configs(run_folder, range_V_S, solver, population_size, generations, sigma_init, seeds, elapsed_time):
    header = ["range_V_S", "Solver", "Population_Size", "Max_Generations", "Sigma_Init", "Seeds", "Elapsed_Time"]
    data = [range_V_S, solver, population_size, generations, sigma_init, seeds, elapsed_time]
    
    with open(run_folder + '/configs.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        writer.writerow(header)
        writer.writerow(data)


if __name__ == "__main__":
    
    start_time = time.time()
    
    file = open('./data/b_series.json')
    b_series = json.load(file)
     
    range_V_S = [7.0, 7.5, 8.0, 8.5]
    # range_V_S = [7.0]
    solver = Solver.CMA_ES
    population_size = 5
    generations = None
    sigma_init = 0.1
    seeds = 10
    
    datetime_now = datetime.now()
    run_folder = 'results/' + str(solver.name) + '-' + datetime_now.strftime("%m_%d-%H_%M")
    
    os.mkdir(run_folder)
    
    for V_S in range_V_S:
        
        V_S_str = str(V_S).replace('.', '_')
        vS_folder = run_folder + '/' + V_S_str
        
        os.mkdir(vS_folder)
    
        # #TODO: implement paralelism 
        for Z in range(b_series['range_Z'][0], b_series['range_Z'][1] + 1):
        
            Z_str = str(Z)
            Z_folder = vS_folder + '/' + Z_str
        
            os.mkdir(Z_folder)
        
            es = EvolutionaryStrategy(solver, 
                                    max_generations=generations, 
                                    population_size=population_size, 
                                    service_speed=V_S,
                                    qtde_seeds=seeds, 
                                    sigma_init=sigma_init,
                                    b_series_json=b_series, 
                                    number_of_blades=Z,
                                    run_folder=vS_folder)
            es.run_solver()
            
            df = pd.DataFrame(es.valid_solutions)
            
            df.to_csv(Z_folder + '/valids.csv', index=False)

    end_time = time.time()
    
    elapsed_time = (end_time - start_time) / 60
    # print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
    print(f"Tempo decorrido: {int(elapsed_time)} minutos")

    save_run_configs(run_folder, range_V_S, solver, population_size, generations, sigma_init, seeds, elapsed_time)

    print()

    print("vS | P_B | Z | D | AEdAO | PdD")
    
    has_valids, min_pb_row = get_best(run_folder + '/7_0/all_results.csv')
    if has_valids: print("7.0", min_pb_row.iloc[5], min_pb_row.iloc[1], min_pb_row.iloc[2], min_pb_row.iloc[3], min_pb_row.iloc[4])
    
    has_valids, min_pb_row = get_best(run_folder + '/7_5/all_results.csv')
    if has_valids: print("7.5", min_pb_row.iloc[5], min_pb_row.iloc[1], min_pb_row.iloc[2], min_pb_row.iloc[3], min_pb_row.iloc[4])
    
    has_valids, min_pb_row = get_best(run_folder + '/8_0/all_results.csv')
    if has_valids: print("8.0", min_pb_row.iloc[5], min_pb_row.iloc[1], min_pb_row.iloc[2], min_pb_row.iloc[3], min_pb_row.iloc[4])
    
    has_valids, min_pb_row = get_best(run_folder + '/8_5/all_results.csv')
    if has_valids: print("8.5", min_pb_row.iloc[5], min_pb_row.iloc[1], min_pb_row.iloc[2], min_pb_row.iloc[3], min_pb_row.iloc[4])

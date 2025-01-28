import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from classes import File_Reader

general_csv_file = os.path.join("csv", "video_maker.csv")
# Carica il file CSV
df = pd.read_csv(general_csv_file, delimiter=';')

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

arena_area = values_dictionary['width_arena'] * values_dictionary['height_arena']
number_of_robots = values_dictionary['robot_number']
threshold = values_dictionary['threshold']

def phase_synchrony(sim_data):
    
    """
    Compute phase synchronization ∆Θ(t) for a dataset.
    """
    
    ms_values = sim_data['ms'].unique()
    synchrony_values = []

    for ms in ms_values:
        current_data = sim_data[sim_data['ms'] == ms]
        phases = current_data['phase'].values
        M = len(phases)

        # compute ∆Θ(t)
        total_diff = 0
        num_pairs = 0

        for i in range(M):
            for j in range(i + 1, M):
                diff = abs(phases[i] - phases[j])
                cyclic_diff = min(diff, 2 * np.pi - diff)  # Normalizza in [0, π]
                total_diff += cyclic_diff 
                num_pairs += 1
        
        # Value normalization
        max_diff = num_pairs * np.pi  # Massima differenza possibile
        delta_theta = (total_diff / max_diff) if num_pairs > 0 else 0
        synchrony_values.append((ms, delta_theta))

    return synchrony_values 

# Ottieni i numeri univoci delle simulazioni
simulation_numbers = df['simulation number'].unique()
    
# Itera su ogni simulazione
for sim_number in simulation_numbers:
    # Filtra i dati per la simulazione corrente
    sim_data = df[df['simulation number'] == sim_number]
    synchrony = phase_synchrony(sim_data)
    # Estrai i valori di tempo e ∆Θ(t)
    ms_values, delta_theta_values = zip(*synchrony)
    # Plot della sincronizzazione
    plt.plot(ms_values, delta_theta_values, label=f'Simulation {sim_number}')

# Configurazione del grafico
plt.xlabel('Time (ms)')
plt.ylabel('Phase Synchrony ∆Θ(t)')
plt.title('Phase Synchrony Over Time')
plt.legend()
plt.grid(True)
plt.show()

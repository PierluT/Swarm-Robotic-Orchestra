import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns
import glob

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

# Cerca tutti i file video.csv nelle sottocartelle di "csv"
csv_files = glob.glob("csv/**/video.csv", recursive=True)

# Lista per salvare tutti i dati
all_results = []

# Debug: Verifica che siano stati trovati file
print(f"Files trovati: {len(csv_files)}")

for file_path in csv_files:
    # Estrai il nome della cartella superiore (dove si trova il file)
    folder_name = os.path.basename(os.path.dirname(file_path))
    
    # Estrarre il numero di robot dal nome della cartella
    parts = folder_name.split("R_N")
    if len(parts) > 1:
        num_robots = int(parts[1].split("_")[0])  # Prende il numero dopo "R_N"
    else:
        continue  # Se il nome non è nel formato giusto, salta il file

    # Leggi il CSV
    df = pd.read_csv(file_path, delimiter=';')
    df['simulation number'] = df['simulation number'].astype(int)

    # Analizza ogni simulazione nel file
    simulation_numbers = df['simulation number'].unique()
    
    for sim_number in simulation_numbers:
        sim_data = df[df['simulation number'] == sim_number]
        synchrony = phase_synchrony(sim_data)
        
        # Raggruppiamo i dati per intervalli di tempo (6000 ms per ogni intervallo)
        for ms, delta_theta in synchrony:
            time_interval = (ms // 6000) * 6000  # Rende l'intervallo di tempo una cifra divisibile per 6000
            time_interval_seconds = time_interval / 1000  # Conversione in secondi
            all_results.append({
                'Time Interval (s)': time_interval_seconds,
                'Phase Synchrony (∆Θ)': delta_theta,
                'Num Robots': num_robots
            })

# Creare un DataFrame aggregato
results_df = pd.DataFrame(all_results)

# Verifica se la colonna 'Time Interval (s)' esiste
if 'Time Interval (s)' not in results_df.columns:
    print("La colonna 'Time Interval (s)' non è presente nel DataFrame!")
else:
    print(f"Le colonne nel DataFrame: {results_df.columns}")

# Debug: Verifica che ci siano effettivamente più configurazioni di robot
print(f"Numero di righe nel DataFrame: {len(results_df)}")
print(f"Valori unici di 'Num Robots': {results_df['Num Robots'].unique()}")

# Definire i colori personalizzati per i gruppi
palette = {5: 'blue', 10: 'orange', 15: 'green'}

# BOX PLOT: Confronto tra numero di robot e sincronizzazione di fase
plt.figure(figsize=(12, 6))
sns.boxplot(x='Time Interval (s)', y='Phase Synchrony (∆Θ)', hue='Num Robots', data=results_df, palette=palette)
plt.title('Evoluzione della Sincronizzazione di Fase in funzione dell\'Intervallo Temporale')
plt.xlabel('Intervallo Temporale (s)')
plt.ylabel('Sincronizzazione di Fase (∆Θ)')
plt.grid(True)
plt.legend(title='Numero di Robot', loc='upper right')
plt.xticks(rotation=45)  # Ruotare le etichette dell'asse x per una migliore visibilità
plt.show()

# Esportare i dati aggregati per ulteriori analisi (opzionale)
results_df.to_csv("synchrony_analysis_time_intervals_seconds.csv", index=False)
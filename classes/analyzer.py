import os
import pandas as pd
import numpy as np
import re
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from collections import Counter
import re

class DataAnalyzer:
    
    def __init__(self, analysis_function=None):
        
        self.csv_directory = ""
        self.analysis_function = analysis_function  # generic analysis function

    def get_csv_files(self):
        """Trova tutti i file video.csv nelle sottocartelle di 'csv/'"""
        return glob.glob("csv/S_N*_R_N*_BPM*_timbres_number*/video.csv", recursive=True)

    def extract_parameter_from_folder(self, folder_path, parameter_name):
        """
        Estrae il valore numerico di un parametro (es. 'R_N_15') dal nome della cartella.

        :param folder_path: Percorso completo della cartella.
        :param parameter_name: Il nome del parametro da cercare (es. 'R_N').
        :return: Il valore intero del parametro se trovato, altrimenti None.
        """
        folder_name = os.path.basename(folder_path)
        pattern = rf"{parameter_name}_(\d+)"
        match = re.search(pattern, folder_name)
        if match:
            return int(match.group(1))
        return None
    
    def timbre_trend_per_robot_count(self, step_size=15000):
        all_data = []
        csv_files = self.get_csv_files()

        for file_path in csv_files:
            try:
                df = pd.read_csv(file_path, delimiter=";")
            except Exception as e:
                print(f"❌ Errore nel file {file_path}: {e}")
                continue

            folder = os.path.dirname(file_path)
            num_robots = self.extract_parameter_from_folder(folder, "R_N")

            if num_robots is None:
                print(f"⚠️ Numero di robot non trovato in {folder}")
                continue

            df['time_bin'] = ((df['ms'] // step_size) * step_size) / 1000  # bin in secondi

            latest_timbre = df.sort_values(by='ms').groupby(['simulation number', 'robot number', 'time_bin']).last().reset_index()

            timbre_counts = latest_timbre.groupby(['simulation number', 'time_bin', 'timbre']).size().reset_index(name='count')
            timbre_counts['percentage'] = timbre_counts['count'] / num_robots
            timbre_counts['number_of_robots'] = num_robots

            all_data.append(timbre_counts)

        if not all_data:
            print("❌ Nessun dato disponibile.")
            return

        final_df = pd.concat(all_data)

        unique_robot_counts = sorted(final_df['number_of_robots'].unique())
        num_plots = len(unique_robot_counts)

        plt.figure(figsize=(16, 5 * num_plots))

        for i, robot_count in enumerate(unique_robot_counts, 1):
            plt.subplot(num_plots, 1, i)
            subset = final_df[final_df['number_of_robots'] == robot_count]
            sns.boxplot(x="time_bin", y="percentage", hue="timbre", data=subset, palette="Set2")
            plt.axhline(0.6, ls='--', color='gray', label='TpC desired (60%)')
            plt.axhline(0.2, ls='--', color='gray', label='BTb/Tbn desired (20%)')
            plt.title(f"Timbres evolution for - {robot_count} robots", fontsize=10, pad=20)
            plt.xlabel("Time (s)", fontsize=8, labelpad=20, loc='left')
            plt.ylabel("Robot percentage per timbre", fontsize=8)
            plt.legend(title="Timbre", loc="upper right")

        plt.subplots_adjust(hspace=0.5, left=0.1)
        plt.tight_layout()
        plt.show()

    def timbre_analysis_across_robots(self):
         all_results = []
 
         # Trova tutti i file CSV nelle cartelle specificate
         csv_files = self.get_csv_files()
 
         for file_path in csv_files:
             num_robots = self.extract_robot_number(file_path)
             if num_robots is None:
                 continue  # Salta file non validi
 
             # Carica il file CSV
             df = pd.read_csv(file_path, delimiter=";")
 
             # Ordina per numero di simulazione, robot number e millisecondo
             df_sorted = df.sort_values(by=['simulation number', 'robot number', 'ms'], ascending=[True, True, False])
 
             # Prendi l'ultimo millisecondo per ogni robot in ogni simulazione
             last_millisecond_per_robot = df_sorted.drop_duplicates(subset=['simulation number', 'robot number'], keep='first')
 
             # Conta i timbri per ogni simulazione
             timbre_counts = last_millisecond_per_robot.groupby("simulation number")['timbre'].value_counts().unstack(fill_value=0)
 
             # Aggiungi una colonna per il numero di robot
             timbre_counts['Num Robots'] = num_robots
 
             all_results.append(timbre_counts)
 
         # Unisce tutti i DataFrame raccolti
         if not all_results:
             print("Nessun dato disponibile per l'analisi dei timbri.")
             return
 
         final_df = pd.concat(all_results)
 
         # Boxplot per visualizzare la distribuzione dei timbri nei diversi setup di robot
         plt.figure(figsize=(12, 6))
         sns.boxplot(data=final_df.melt(id_vars=['Num Robots'], var_name='Timbre', value_name='Count'),
                     x='Timbre', y='Count', hue='Num Robots', palette='Set1')
 
         # Etichette del grafico
         plt.title('Distribuzione dei Timbri nelle Simulazioni')
         plt.xlabel('Timbre')
         plt.ylabel('Conteggio')
         plt.legend(title='Num Robots', loc='upper right')
         plt.xticks(rotation=45, ha='right')
 
         # Mostra il grafico
         plt.tight_layout()
         plt.show()

def harmony_consensus(sim_data):
    """
    Compute harmony consensus H(t) for a dataset.
    H(t) is the proportion of robots whose pitches belong to at least a single common scale.
    """
    ms_values = sim_data['ms'].unique()
    harmony_values = []

    for ms in ms_values:
        current_data = sim_data[sim_data['ms'] == ms]
        M = len(current_data)

        if M == 0:
            continue

        # Conta quanti robot hanno harmony = True
        harmony_count = current_data['harmony'].sum()  # Conta i True (che sono considerati come 1)
        
        # Normalizzazione tra 1/M e 1
        H_t = max(1/M, harmony_count / M)
        
        harmony_values.append((ms, H_t))

    return harmony_values

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

"""
analyzer = DataAnalyzer(analysis_function = None)
a = analyzer.get_csv_files()
folder_path = os.path.dirname(a[0])
print("File CSV trovati:", folder_path)
print(analyzer.extract_parameter_from_folder(folder_path, "timbres_number"))
# Analisi per il numero di timbri
#analyzer.timbre_trend_boxplot()
#csv_files = analyzer.get_csv_files()
#print("File CSV trovati:", csv_files)
analyzer.timbre_analysis_across_robots()
#analyzer.analyze_timbre_distribution_over_time()
#analyzer.analyze()    
#print(analyzer.get_csv_files())
#print(analyzer.extract_robot_number(analyzer.get_csv_files())) #

"""
analyzer = DataAnalyzer(analysis_function = None)
analyzer.timbre_trend_per_robot_count()


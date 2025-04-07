import os
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from collections import Counter

class DataAnalyzer:
    def __init__(self, analysis_function=None):
        self.csv_directory = "csv/harmony_consensous/robot_numbers_values"
        self.time_conversion_factor = 1000
        self.analysis_function = analysis_function  # Funzione di analisi generica
        self.results_df = None

    def get_csv_files(self):
        """Trova tutti i file video.csv nelle sottocartelle di 'csv/'"""
        return glob.glob("csv/S_N*R_N*BPM*timbres_number*/video.csv", recursive=True)

    def extract_robot_number(self, file_path):
        """Estrae il numero di robot dal nome della cartella del file CSV."""
        folder_name = os.path.basename(os.path.dirname(file_path))
        parts = folder_name.split("R_N")
        if len(parts) > 1:
            return int(parts[1].split("_")[0])  # Prende il numero dopo "R_N"
        return None

    def extract_parameter_from_folder(self, folder_path, parameter_name):
        """
        Estrae il valore di un parametro (es. "timbres_number") dal nome della cartella.
        """
        folder_name = os.path.basename(folder_path)
        parts = folder_name.split(f"{parameter_name}")
        
        if len(parts) > 1:
            try:
                return int(parts[1].split("_")[0])  # Prende il numero dopo il parametro
            except ValueError:
                return None
        return None
    
    def analyze_parameter(self, parameter_name):
        """
        Analizza la distribuzione dei timbri o di altri parametri (es. numero di robot, BPM, lambda, etc.).
        
        :param parameter_name: Nome del parametro da analizzare (es. "timbres_number", "Num Robots").
        """
        all_results = []

        csv_folders = glob.glob(f"csv/S_N*R_N*BPM*lambda*timbres_number*")  # Trova tutte le cartelle

        for folder in csv_folders:
            param_value = self.extract_parameter_from_folder(folder, parameter_name)  # Estrai il valore del parametro
            if param_value is None:
                continue

            csv_path = os.path.join(folder, "video.csv")  # Percorso del file CSV
            if not os.path.exists(csv_path):
                continue  # Salta se il file non esiste

            df = pd.read_csv(csv_path, delimiter=";")
            df_sorted = df.sort_values(by=['simulation number', 'robot number', 'ms'], ascending=[True, True, False])
            last_millisecond_per_robot = df_sorted.drop_duplicates(subset=['simulation number', 'robot number'], keep='first')

            # Conta i timbri per ogni simulazione
            timbre_counts_per_simulation = last_millisecond_per_robot.groupby("simulation number")['timbre'].value_counts().unstack(fill_value=0)
            timbre_counts_per_simulation[parameter_name] = param_value  # Aggiunge il valore del parametro come colonna

            all_results.append(timbre_counts_per_simulation)

        if not all_results:
            print(f"Nessun dato disponibile per l'analisi del parametro: {parameter_name}")
            return

        # Unisce tutti i DataFrame
        combined_df = pd.concat(all_results)

        # Creazione del DataFrame in formato lungo
        df_long = combined_df.reset_index().melt(id_vars=[parameter_name], var_name="Timbre", value_name="Count")

        # Se il parametro è "timbres_number", correggi il nome della colonna per coerenza con i dati
        if parameter_name == "timbres_number":
            df_long.rename(columns={"Timbre": "timbre"}, inplace=True)

        # Creazione del boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=parameter_name, y="Count", data=df_long, palette='Set2')

        # Aggiungi etichette al grafico
        plt.title(f'Distribuzione Timbri per {parameter_name}')
        plt.xlabel(parameter_name)
        plt.ylabel('Count')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    def timbre_trend_boxplot(self, step_size=15000):
        """
        Mostra l'evoluzione della percentuale dei timbri nel tempo (normalizzata per robot),
        con linee tratteggiate che indicano la distribuzione attesa (TpC=60%, altri=20%).
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd

        all_data = []

        csv_files = self.get_csv_files()

        for file_path in csv_files:
            df = pd.read_csv(file_path, delimiter=";")
            df['time_bin'] = ((df['ms'] // step_size) * step_size) / 1000  # tempo in secondi

            # Prendiamo il timbro più recente di ogni robot in ogni intervallo di tempo
            latest_timbre = df.sort_values(by='ms').groupby(['simulation number', 'robot number', 'time_bin']).last().reset_index()

            # Conta i timbri per ciascun intervallo e normalizza (10 robot = totale 1.0)
            timbre_counts = latest_timbre.groupby(['simulation number', 'time_bin', 'timbre']).size().reset_index(name='count')
            timbre_counts['percentage'] = timbre_counts['count'] / 10  # perché ci sono 10 robot

            all_data.append(timbre_counts)

        if not all_data:
            print("Nessun dato disponibile per l'analisi.")
            return

        final_df = pd.concat(all_data)

        plt.figure(figsize=(18, 8))
        sns.boxplot(x="time_bin", y="percentage", hue="timbre", data=final_df, palette="Set2")

        # Linee tratteggiate per percentuali attese
        #plt.axhline(0.6, ls='--', color='gray', label='TpC desired (60%)')
        #plt.axhline(0.2, ls='--', color='gray', label='BTb/Tbn desired (20%)')

        plt.title('Percentage Distribution of timbre Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Percentage of Robots per timbre')
        plt.xticks(rotation=45)
        plt.legend(title='Timbre', loc='upper right')
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

#analyzer = DataAnalyzer(analysis_function = None)
# Analisi per il numero di timbri
#analyzer.timbre_trend_boxplot()
#csv_files = analyzer.get_csv_files()
#print("File CSV trovati:", csv_files)
#analyzer.timbre_analysis_across_robots()
#analyzer.analyze_timbre_distribution_over_time()
#analyzer.analyze()    
#print(analyzer.get_csv_files())
#print(analyzer.extract_robot_number(analyzer.get_csv_files())) 

"""
#  PLOT METHODS FOR TIMBRE ALLOCATION
    
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

    
        """
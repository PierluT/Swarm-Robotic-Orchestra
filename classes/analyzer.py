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
        return glob.glob("csv/S_N*R_N*BPM*lambda*timbres_number*/video.csv", recursive=True)

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


    def timbre_analysis_across_robots(self):
        """
        Analizza la distribuzione dei timbri finali su più cartelle e confronta i boxplot per diversi R_N.
        """
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

            # Salva i risultati
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
        plt.title('Timbre distribution for different robot groups')
        plt.xlabel('Timbre')
        plt.ylabel('Count')
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

#analyzer = DataAnalyzer(analysis_function = None)
# Analisi per il numero di timbri
#analyzer.analyze_parameter("timbres_number")
#csv_files = analyzer.get_csv_files()
#print("File CSV trovati:", csv_files)
#analyzer.timbre_analysis_across_robots()

#analyzer.analyze()    
#print(analyzer.get_csv_files())
#print(analyzer.extract_robot_number(analyzer.get_csv_files())) 




"""
#  PLOT METHODS FOR TIMBRE ALLOCATION
    def timbre_analysis_distribution(self, csv_path):
        # Carica il file CSV
        df = pd.read_csv(csv_path, delimiter=";")

        # Ordina per numero di simulazione, robot number e millisecondo
        df_sorted = df.sort_values(by=['simulation number', 'robot number', 'ms'], ascending=[True, True, False])

        # Prendi l'ultimo millisecondo per ogni robot in ogni simulazione
        last_millisecond_per_robot = df_sorted.drop_duplicates(subset=['simulation number', 'robot number'], keep='first')

        #print(last_millisecond_per_robot)
        # Conta i timbri per ogni simulazione
        timbre_counts_per_simulation = last_millisecond_per_robot.groupby("simulation number")['timbre'].value_counts().unstack(fill_value=0)
        #print(timbre_counts_per_simulation)
        # Calcola la media della distribuzione dei timbri su tutte le simulazioni
        avg_timbre_counts = timbre_counts_per_simulation.mean()

        # Visualizza il risultato
        print(avg_timbre_counts)
        
        avg_timbre_counts.plot(kind='bar', color='skyblue')

        # Aggiungi etichette al grafico
        plt.title('Distribuzione Media dei Timbri su Più Simulazioni')
        plt.xlabel('Timbro')
        plt.ylabel('Conteggio Medio')
        plt.xticks(rotation=45, ha='right')

        # Mostra il grafico
        plt.tight_layout()
        plt.show()"
   
        """
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
        self.interval_size = 6000
        self.analysis_function = analysis_function  # Funzione di analisi generica
        self.results_df = None

    #  PLOT METHODS FOR TIMBRE ALLOCATION
    def timbre_analysis_distribution(self, csv_path):
        """
            Legge il CSV, estrae i timbri finali di ogni simulazione e mostra un grafico a barre con la distribuzione.
            
            :param csv_path: Percorso del file CSV da analizzare.
        """
        """
        Analizza la distribuzione media dei timbri finali considerando più simulazioni in un unico CSV.

        :param csv_path: Percorso del file CSV contenente i dati di tutte le simulazioni.
        """
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
        plt.show()  
    
    def get_csv_files(self):
        """Trova tutti i file CSV nella directory specificata."""
        return glob.glob(f"{self.csv_directory}/**/video.csv", recursive=True)

    def extract_robot_number(self, file_path):
        """Estrae il numero di robot dal nome della cartella del file CSV."""
        folder_name = os.path.basename(os.path.dirname(file_path))
        parts = folder_name.split("R_N")
        if len(parts) > 1:
            return int(parts[1].split("_")[0])  # Prende il numero dopo "R_N"
        return None

    def process_simulation(self, df, num_robots):
        """Processa i dati di simulazione, applicando la funzione di analisi e aggregando i risultati."""
        all_results = []
        simulation_numbers = df['simulation number'].unique()

        for sim_number in simulation_numbers:
            sim_data = df[df['simulation number'] == sim_number]
            # Usa la funzione di analisi generica passata all'inizio
            analysis_results = self.analysis_function(sim_data)

            for ms, value in analysis_results:
                # Rende l'intervallo di tempo divisibile per interval_size
                time_interval = (ms // self.interval_size) * self.interval_size
                time_interval_seconds = time_interval / self.time_conversion_factor  # Conversione in secondi
                all_results.append({
                    'Time Interval (s)': time_interval_seconds,
                    'Value': value,  # Il valore analizzato
                    'Num Robots': num_robots
                })

        return all_results

    def aggregate_results(self):
        """Aggrega i risultati di tutte le simulazioni in un DataFrame."""
        all_results = []
        csv_files = self.get_csv_files()

        for file_path in csv_files:
            num_robots = self.extract_robot_number(file_path)
            if num_robots is None:
                continue

            df = pd.read_csv(file_path, delimiter=';')
            df['simulation number'] = df['simulation number'].astype(int)

            simulation_results = self.process_simulation(df, num_robots)
            all_results.extend(simulation_results)

        self.results_df = pd.DataFrame(all_results)

    def plot_boxplot(self, value_label='Value'):
        """Crea il boxplot per visualizzare l'evoluzione dei valori analizzati nel tempo."""
        plt.figure(figsize=(12, 6))
        
        sns.boxplot(
            x='Time Interval (s)', 
            y=value_label, 
            hue='Num Robots',  # Differenzia i gruppi in base al numero di robot
            data=self.results_df, 
            palette='Set1'  # Colori diversi per i gruppi
        )

        plt.title('Harmony Consensus Evolution')
        plt.xlabel('Time Interval (s)')
        plt.ylabel(f'{value_label} (H(t) o altro)')
        plt.grid(True)
        plt.legend(title='Num Robots', loc='upper right')
        plt.xticks(rotation=45)

        # Creare la cartella "plot" se non esiste
        plot_directory = "plot"
        if not os.path.exists(plot_directory):
            os.makedirs(plot_directory)

        # Salva il grafico nella cartella "plot"
        plot_filename = os.path.join(plot_directory, "robot_number_analysis_plot.png")
        plt.savefig(plot_filename)

        # Mostra il grafico
        plt.show()

    def analyze(self):
        """Metodo principale che esegue l'intero processo di analisi e crea il boxplot."""
        # Aggrega i risultati
        self.aggregate_results()

        # Verifica se la colonna 'Time Interval (s)' esiste
        if 'Time Interval (s)' not in self.results_df.columns:
            print("La colonna 'Time Interval (s)' non è presente nel DataFrame!")
        else:
            print(f"Le colonne nel DataFrame: {self.results_df.columns}")

        # Debug: Verifica che ci siano effettivamente più configurazioni di numero di robot
        print(f"Numero di righe nel DataFrame: {len(self.results_df)}")
        #print(f"Valori unici di 'Num Robots': {self.results_df['Num Robots'].unique()}")

        # Crea il boxplot
        self.plot_boxplot()

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

    

analyzer = DataAnalyzer(analysis_function = phase_synchrony)
print(analyzer.get_csv_files())
#analyzer.analyze()    
#print(analyzer.get_csv_files())
#print(analyzer.extract_robot_number(analyzer.get_csv_files())) 
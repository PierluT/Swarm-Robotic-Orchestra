import os
import pandas as pd
import numpy as np
import re
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from collections import Counter
from configparser import ConfigParser
from scipy.special import rel_entr
import re
from scipy.stats import entropy
from sklearn.metrics import mean_squared_error
from dictionaries import colours, major_scales, major_pentatonic_scales, whole_tone_scales, orchestra_to_midi_range, instrument_ensembles, instrument_target_distributions_full, ensemble_names 

class DataAnalyzer:
    
    def __init__(self):
        self.csv_directory = ""
        self.timbre_dictionary = orchestra_to_midi_range
        self.timbre_list = [instrument for instruments in self.timbre_dictionary.values() for instrument in instruments]
        self.distribution_dictionary = instrument_target_distributions_full

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
    
    def timbre_trend_across_configs(self, base_dir="csv", step_size=30000):
        all_data = []
        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            video_csv = os.path.join(folder_path, "video.csv")

            if not os.path.exists(video_csv):
                continue

            try:
                df = pd.read_csv(video_csv, delimiter=";")
            except Exception as e:
                print(f"❌ Errore nel file {video_csv}: {e}")
                continue

            # Estrai delta e numero di robot dalla cartella
            try:
                parts = folder.split("_")
                delta = int(parts[parts.index("delta") + 1])
                num_robots = int(parts[parts.index("R") + 2])
            except Exception as e:
                print(f"⚠️ Parametri non trovati in {folder}: {e}")
                continue

            df['time_bin'] = ((df['ms'] // step_size) * step_size) / 1000

            latest_timbre = df.sort_values(by='ms').groupby(
                ['simulation number', 'robot number', 'time_bin']
            ).last().reset_index()

            timbre_counts = latest_timbre.groupby(
                ['simulation number', 'time_bin', 'timbre']
            ).size().reset_index(name='count')

            timbre_counts['percentage'] = timbre_counts['count'] / num_robots
            timbre_counts['delta'] = delta
            timbre_counts['robots'] = num_robots
            timbre_counts['config'] = f"R{num_robots}_d{delta}"

            all_data.append(timbre_counts)

        if not all_data:
            print("❌ Nessun dato valido.")
            return

        final_df = pd.concat(all_data)
        unique_configs = sorted(final_df['config'].unique())
        num_plots = len(unique_configs)

        fig, axes = plt.subplots(num_plots, 1, figsize=(16, 5 * num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes]

        for ax, config in zip(axes, unique_configs):
            subset = final_df[final_df['config'] == config]
            sns.boxplot(
                x="time_bin", y="percentage", hue="timbre", data=subset,
                hue_order=self.timbre_list,
                palette="tab20", ax=ax
            )
            ax.set_title(f"set up: {config}", fontsize=8, pad=15)
            ax.set_xlabel("Time (s)", fontsize=12)
            ax.set_ylabel("robot per timbre", fontsize=8)
            ax.legend_.remove()

        # Legenda unica e orizzontale
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(
            handles, labels, title="Timbre", loc="lower center",
            ncol=len(self.timbre_list),  # Legenda su una sola riga
            bbox_to_anchor=(0.5, -0.01), fontsize=12, title_fontsize=13
        )

        # Migliora la disposizione evitando sovrapposizioni
        plt.subplots_adjust(hspace=0.4)  # più spazio tra i grafici
        plt.tight_layout(rect=[0, 0.05, 1, 1])  # lascia spazio per la legenda
        plt.show()

    def timbre_variance_and_entropy(self, base_dir="csv", step_size=4000):
        results = []

        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            video_csv = os.path.join(folder_path, "video.csv")

            if not os.path.exists(video_csv):
                continue

            try:
                df = pd.read_csv(video_csv, delimiter=";")
            except Exception as e:
                print(f"❌ Errore nel file {video_csv}: {e}")
                continue

            try:
                parts = folder.split("_")
                delta = int(parts[parts.index("delta") + 1])
                num_robots = int(parts[parts.index("R") + 2])
                beats = int(parts[parts.index("beats") + 1])
            except Exception as e:
                print(f"⚠️ Parametri non trovati in {folder}: {e}")
                continue

            # Target distribution in base al rapporto robot/beats
            try:
                ratio = num_robots // beats
                target_dist = instrument_target_distributions_full[ratio]
                target_timbres = list(target_dist.keys())
                target_probs = np.array([target_dist[t] for t in target_timbres])
                print(f"Target timbres: {target_timbres}")
                ideal_entropy = entropy(target_probs, base=2)
                ideal_variance = np.var(target_probs)
            except KeyError:
                print(f"⚠️ Nessuna distribuzione target per il rapporto {num_robots}/{beats} (={ratio})")
                continue

            df['time_bin'] = ((df['ms'] // step_size) * step_size) / 1000

            latest = df.sort_values(by='ms').groupby(['simulation number', 'robot number', 'time_bin']).last().reset_index()
            grouped = latest.groupby(['simulation number', 'time_bin', 'timbre']).size().reset_index(name='count')
            grouped['percentage'] = grouped['count'] / num_robots

            for (sim, time_bin), group in grouped.groupby(['simulation number', 'time_bin']):
                observed = group.set_index('timbre')['percentage'].reindex(target_timbres, fill_value=0.0)
                var = observed.var()
                kl = entropy(observed.values, target_probs, base=2)


                results.append({
                    "simulation": sim,
                    "time_bin": time_bin,
                    "delta": delta,
                    "robots": num_robots,
                    "variance": var,
                    "kl_divergence": kl,
                    "ideal_entropy": ideal_entropy,
                    "ideal_variance": ideal_variance,
                    "config": f"R{num_robots}_d{delta}_b{beats}"
                })

        if not results:
            print("❌ Nessun dato valido.")
            return

        df_results = pd.DataFrame(results)

        # 🎨 Plot
        fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

        # VARIANZA
        sns.lineplot(data=df_results, x="time_bin", y="variance", hue="config", ax=axes[0])
        for config, group in df_results.groupby("config"):
            axes[0].axhline(y=group["ideal_variance"].iloc[0], linestyle="--", color="gray", alpha=0.5)
        axes[0].set_title("Variance (Filtered on Target Timbres) Over Time")
        axes[0].set_ylabel("Variance")

        # KL DIVERGENCE
        sns.lineplot(data=df_results, x="time_bin", y="kl_divergence", hue="config", ax=axes[1])

        # ⚠️ RIMUOVI questa linea: l'ideale di KL divergence è sempre 0 (nessuna differenza con la distribuzione target)
        # quindi aggiungerla come linea orizzontale non ha senso informativo.
        # for config, group in df_results.groupby("config"):
        #     axes[1].axhline(y=group["ideal_entropy"].iloc[0], linestyle="--", color="gray", alpha=0.5)

        axes[1].set_title("Kullback-Leibler Divergence vs Target Timbre Distribution Over Time")
        axes[1].set_ylabel("KL Divergence (base 2)")
        axes[1].set_xlabel("Time (s)")

        plt.tight_layout()
        plt.show()

    def timbre_mse_over_time(self, base_dir="csv", step_size=1000):
        results = []

        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            video_csv = os.path.join(folder_path, "video.csv")

            if not os.path.exists(video_csv):
                continue

            try:
                df = pd.read_csv(video_csv, delimiter=";")
            except Exception as e:
                print(f"❌ Errore nel file {video_csv}: {e}")
                continue

            # 📦 Estrai parametri dal nome della cartella
            try:
                parts = folder.split("_")
                delta = int(parts[parts.index("delta") + 1])
                num_robots = int(parts[parts.index("R") + 2])
                beats = int(parts[parts.index("beats") + 1])
            except Exception as e:
                print(f"⚠️ Parametri non trovati in {folder}: {e}")
                continue

            df['time_bin'] = ((df['ms'] // step_size) * step_size) / 1000

            latest = df.sort_values(by='ms').groupby(['simulation number', 'robot number', 'time_bin']).last().reset_index()
            grouped = latest.groupby(['simulation number', 'time_bin', 'timbre']).size().reset_index(name='count')
            grouped['percentage'] = grouped['count'] / num_robots

            # 🎯 Calcola la chiave per target finale: robot / beats
            try:
                ratio = num_robots // beats
                target_dist = instrument_target_distributions_full[ratio]
            except KeyError:
                print(f"⚠️ Nessuna distribuzione target per il rapporto {num_robots}/{beats} (={ratio})")
                continue

            # 🧪 MSE per ogni time_bin
            for (sim, time_bin), group in grouped.groupby(['simulation number', 'time_bin']):
                observed = group.set_index('timbre')['percentage'].reindex(self.timbre_list, fill_value=0.0)
                target = [target_dist.get(t, 0.0) for t in self.timbre_list]

                mse = mean_squared_error(target, observed.values)
                rmse_percent = (np.sqrt(mse) * 100)
                ensemble_number = num_robots // beats
                ensemble_label = ensemble_names.get(ensemble_number, f"{ensemble_number}-group")

                results.append({
                    "simulation": sim,
                    "time_bin": time_bin,
                    "delta": delta,
                    "robots": num_robots,
                    "beats": beats,
                    "mse": mse,
                    "rmse_percent": rmse_percent,
                    "config": f"{ensemble_label},delta = {delta})"
                })

        if not results:
            print("❌ Nessun dato valido.")
            return

        df_results = pd.DataFrame(results)

        # 📊 Plot con annotazione del minimo MSE per configurazione
        plt.figure(figsize=(16, 6))
        ax = sns.lineplot(data=df_results, x="time_bin", y="mse", hue="config", ci=None)

        # Annotazioni min MSE per config
        grouped = df_results.groupby("config")["mse"]
        for config, values in grouped:
            min_val = values.min()
            ax.annotate(f"{min_val:.3f}",
                        xy=(df_results["time_bin"].max(), min_val),
                        xytext=(5, 0),
                        textcoords='offset points',
                        va='center',
                        fontsize=9,
                        color='black')
        # Uso del nome nel titolo
        plt.title("Mean Squared Error (MSE) vs Final Target Distribution Over Time")
        plt.xlabel("Time (s)")
        plt.ylabel("MSE (annotated min per config)")
        plt.tight_layout()
        plt.show()

        # 📉 Stampa terminale ultimi valori
        print("\n📊 Ultimi valori di MSE e RMSE% per configurazione:\n")
        last_values = (
            df_results.sort_values("time_bin")
                    .groupby("config")
                    .tail(1)[["config", "time_bin", "mse", "rmse_percent"]]
                    .sort_values(by="mse")
        )

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
analyzer = DataAnalyzer()
#analyzer.timbre_trend_across_configs(base_dir="csv", step_size=30000)
#analyzer.timbre_variance_and_entropy(base_dir="csv", step_size=40)
analyzer.timbre_mse_over_time(base_dir="csv", step_size=4000)
#analyzer.count_perfect_distributions(base_dir="csv", mse_threshold=1e-6, kl_threshold=1e-6)




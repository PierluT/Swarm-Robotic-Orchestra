import os
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from scipy.special import rel_entr
from dictionaries import colours,major_scales, major_pentatonic_scales, whole_tone_scales, SCALE_FAMILIES, orchestra_to_midi_range, instrument_ensembles, instrument_target_distributions_full, ensemble_names 

class DataAnalyzer:
    
    def __init__(self):
        self.csv_directory = ""
        self.timbre_dictionary = orchestra_to_midi_range
        self.timbre_list = [instrument for instruments in self.timbre_dictionary.values() for instrument in instruments]
        self.distribution_dictionary = instrument_target_distributions_full

    def get_csv_files(self):
        """Trova tutti i file video.csv nelle sottocartelle di 'csv/' con naming S_N_..."""
        return glob.glob("csv/S_N_*_R_N_*_BPM_*_min_*_delta_*_beats_*/video.csv", recursive=True)


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
                beats = int(parts[parts.index("beats") + 1])
                ensemble_number = num_robots // beats
                ensemble_label = ensemble_names.get(ensemble_number, f"{ensemble_number}-group")
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
            timbre_counts['config'] = f"{ensemble_label} \u03B4 = {delta}"

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
            ax.set_title(config, fontsize=25, pad=15)
            ax.set_xlabel("Time (s)", fontsize=25)
            ax.set_ylabel("robot per timbre", fontsize=25)
            ax.legend_.remove()

        # Legenda unica e orizzontale
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(
            handles, labels, loc="lower center",
            ncol=len(self.timbre_list),  # Legenda su una sola riga
            bbox_to_anchor=(0.5, -0.01), fontsize=12, title_fontsize=13
        )

        # Migliora la disposizione evitando sovrapposizioni
        plt.subplots_adjust(hspace=0.4)  # più spazio tra i grafici
        plt.tight_layout(rect=[0, 0.05, 1, 1])  # lascia spazio per la legenda
        plt.show()

    def phase_synchrony_boxplot_by_bpm(
        self,
        base_dir="csv",
        step_size=5000,
        fixed_params=None,  # es. {"delta": 100, "beats": 4, "num_robots": 32}
        title="Phase synchrony evolution",
        hue_var="bpm",      # "bpm" oppure "num_robots"
        show=True,
    ):
        if fixed_params is None:
            fixed_params = {}

        def parse_folder_params(folder_name: str):
            parts = folder_name.split("_")

            def get_int_after(token):
                return int(parts[parts.index(token) + 1])

            params = {}

            # BPM / delta / beats
            params["bpm"] = get_int_after("BPM") if "BPM" in parts else None
            params["delta"] = get_int_after("delta") if "delta" in parts else None
            params["beats"] = get_int_after("beats") if "beats" in parts else None

            # num_robots: formato ... R_N_32 ...
            params["num_robots"] = None
            if "R" in parts:
                try:
                    i = parts.index("R")
                    # atteso: parts[i+1] == "N" e parts[i+2] == "<int>"
                    if i + 2 < len(parts):
                        params["num_robots"] = int(parts[i + 2])
                except Exception:
                    pass

            return params

        def to_sync_df(out):
            # out può essere lista di tuple (ms, delta_theta) oppure DataFrame
            if isinstance(out, pd.DataFrame):
                out = out.copy()
                out.columns = [c.strip() for c in out.columns]

                if "delta_theta" not in out.columns and "DeltaTheta" in out.columns:
                    out = out.rename(columns={"DeltaTheta": "delta_theta"})

                if "ms" in out.columns and "delta_theta" in out.columns:
                    return out[["ms", "delta_theta"]].copy()

                # fallback: prime due colonne
                if out.shape[1] >= 2:
                    tmp = out.iloc[:, :2].copy()
                    tmp.columns = ["ms", "delta_theta"]
                    return tmp

                return pd.DataFrame(columns=["ms", "delta_theta"])

            # lista di tuple (ms, delta_theta)
            return pd.DataFrame(out, columns=["ms", "delta_theta"])

        all_data = []

        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            video_csv = os.path.join(folder_path, "video.csv")
            if not os.path.exists(video_csv):
                continue

            params = parse_folder_params(folder)

            # filtra parametri fissi
            skip = False
            for k, v in fixed_params.items():
                if params.get(k) != v:
                    skip = True
                    break
            if skip:
                continue

            try:
                df = pd.read_csv(video_csv, delimiter=";")
                df.columns = [c.strip() for c in df.columns]
            except Exception as e:
                print(f"❌ Errore nel file {video_csv}: {e}")
                continue

            # per-replica se esiste
            if "simulation number" in df.columns:
                sim_groups = df.groupby("simulation number")
            else:
                sim_groups = [(0, df)]

            for sim_id, sim_df in sim_groups:
                try:
                    analyzer = DataAnalyzer()
                    analyzer.df = sim_df
                    out = analyzer.phase_synchrony()  # nessun argomento
                except Exception as e:
                    print(f"❌ phase_synchrony failed for {folder} sim {sim_id}: {e}")
                    continue

                sync_df = to_sync_df(out)
                if sync_df.empty:
                    continue

                # Aggiungi metadati PRIMA del groupby (e poi riaggiungili dopo)
                sync_df["time_bin"] = ((sync_df["ms"] // step_size) * step_size) / 1000.0
                sync_df["bpm"] = params["bpm"]
                sync_df["num_robots"] = params["num_robots"]
                sync_df["delta"] = params["delta"]
                sync_df["beats"] = params["beats"]
                sync_df["simulation number"] = sim_id

                # media per bin
                sync_binned = sync_df.groupby(
                    ["simulation number", "time_bin", "bpm", "num_robots", "delta", "beats"],
                    as_index=False
                )["delta_theta"].mean()

                all_data.append(sync_binned)

        if not all_data:
            print("❌ Nessun dato valido.")
            return None

        final_df = pd.concat(all_data, ignore_index=True)

        # rimuovi righe senza hue_var (es. parsing fallito)
        if hue_var not in final_df.columns:
            raise ValueError(f"hue_var='{hue_var}' not found in final_df columns: {list(final_df.columns)}")
        final_df = final_df.dropna(subset=[hue_var])

        # ----- PLOT stile come la tua immagine -----
        fig, ax = plt.subplots(figsize=(16, 6))

        sns.boxplot(
            data=final_df,
            x="time_bin",
            y="delta_theta",
            hue=hue_var,   # <-- "bpm" o "num_robots"
            dodge=True,
            ax=ax
        )

        ax.set_title(title, fontsize=18)
        ax.set_xlabel("Time Interval (s)", fontsize=14)
        ax.set_ylabel(r"Value ($\Delta\Theta$)", fontsize=14)
        ax.set_ylim(0, 1)

        legend_title = "BPM" if hue_var == "bpm" else "Number of robots"
        ax.legend(title=legend_title, loc="upper right")

        plt.tight_layout()
        if show:
            plt.show()
        else:
            plt.close()

        return final_df

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

    def phase_synchrony(self):
        """
        Compute phase synchronization ΔΘ(t) using self.df.
        Returns: list of (ms, delta_theta)
        """

        if not hasattr(self, "df") or self.df is None:
            raise ValueError("DataAnalyzer.df is not set. Assign a DataFrame to self.df before calling phase_synchrony().")

        sim_data = self.df

        required_cols = {"ms", "beat phase"}
        if not required_cols.issubset(sim_data.columns):
            missing = required_cols - set(sim_data.columns)
            raise ValueError(f"Missing required columns in df: {missing}")

        ms_values = sim_data["ms"].unique()
        synchrony_values = []

        for ms in ms_values:
            current_data = sim_data[sim_data["ms"] == ms]
            phases = current_data["beat phase"].dropna().to_numpy()
            M = len(phases)

            if M < 2:
                synchrony_values.append((ms, 0.0))
                continue

            total_diff = 0.0
            num_pairs = 0

            for i in range(M):
                for j in range(i + 1, M):
                    diff = abs(phases[i] - phases[j])
                    cyclic_diff = min(diff, 2 * np.pi - diff)  # in [0, π]
                    total_diff += cyclic_diff
                    num_pairs += 1

            max_diff = num_pairs * np.pi
            delta_theta = total_diff / max_diff if max_diff > 0 else 0.0
            synchrony_values.append((ms, delta_theta))

        return synchrony_values
    
    def beat_synchrony_boxplot_by_bpm(
        self,
        base_dir="csv",
        step_size=5000,
        fixed_params=None,      # es. {"delta": 100, "beats": 4, "num_robots": 32}
        title="Beat synchrony evolution",
        hue_var="bpm",          # "bpm" oppure "num_robots"
        show=True,
    ):
        if fixed_params is None:
            fixed_params = {}

        def parse_folder_params(folder_name: str):
            parts = folder_name.split("_")

            def get_int_after(token):
                return int(parts[parts.index(token) + 1])

            params = {}
            params["bpm"] = get_int_after("BPM") if "BPM" in parts else None
            params["delta"] = get_int_after("delta") if "delta" in parts else None
            params["beats"] = get_int_after("beats") if "beats" in parts else None

            params["num_robots"] = None
            if "R" in parts:
                try:
                    i = parts.index("R")
                    if i + 2 < len(parts):
                        params["num_robots"] = int(parts[i + 2])
                except Exception:
                    pass

            return params

        # -------- Beat synchrony computation (swarm-level) --------
        def compute_beat_synchrony(df, B_max):
            results = []

            for ms, group in df.groupby("ms"):
                beats = group["beat counter"].dropna().to_numpy()
                M = len(beats)

                if M < 2:
                    results.append((ms, 0.0))
                    continue

                total_diff = 0.0
                num_pairs = 0

                for i in range(M):
                    for j in range(i + 1, M):
                        total_diff += abs(beats[i] - beats[j])
                        num_pairs += 1

                delta_B = (total_diff / num_pairs) / (B_max - 1)
                results.append((ms, delta_B))

            return pd.DataFrame(results, columns=["ms", "delta_B"])

        all_data = []

        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            video_csv = os.path.join(folder_path, "video.csv")
            if not os.path.exists(video_csv):
                continue

            params = parse_folder_params(folder)

            # filtra parametri fissi
            skip = False
            for k, v in fixed_params.items():
                if params.get(k) != v:
                    skip = True
                    break
            if skip:
                continue

            try:
                df = pd.read_csv(video_csv, delimiter=";")
                df.columns = [c.strip() for c in df.columns]
            except Exception as e:
                print(f"❌ Errore nel file {video_csv}: {e}")
                continue

            if "beat counter" not in df.columns:
                print(f"⚠️ Colonna 'beat counter' non trovata in {video_csv}")
                continue

            # per-replica se esiste
            if "simulation number" in df.columns:
                sim_groups = df.groupby("simulation number")
            else:
                sim_groups = [(0, df)]

            for sim_id, sim_df in sim_groups:
                try:
                    sync_df = compute_beat_synchrony(sim_df, params["beats"])
                except Exception as e:
                    print(f"❌ beat_synchrony failed for {folder} sim {sim_id}: {e}")
                    continue

                if sync_df.empty:
                    continue

                # metadati
                sync_df["time_bin"] = ((sync_df["ms"] // step_size) * step_size) / 1000.0
                sync_df["bpm"] = params["bpm"]
                sync_df["num_robots"] = params["num_robots"]
                sync_df["delta"] = params["delta"]
                sync_df["beats"] = params["beats"]
                sync_df["simulation number"] = sim_id

                sync_binned = sync_df.groupby(
                    ["simulation number", "time_bin", "bpm", "num_robots", "delta", "beats"],
                    as_index=False
                )["delta_B"].mean()

                all_data.append(sync_binned)

        if not all_data:
            print("❌ Nessun dato valido.")
            return None

        final_df = pd.concat(all_data, ignore_index=True)

        if hue_var not in final_df.columns:
            raise ValueError(f"hue_var='{hue_var}' not found in final_df columns")

        final_df = final_df.dropna(subset=[hue_var])

        # -------- PLOT --------
        fig, ax = plt.subplots(figsize=(16, 6))

        sns.boxplot(
            data=final_df,
            x="time_bin",
            y="delta_B",
            hue=hue_var,
            dodge=True,
            ax=ax
        )

        ax.set_title(title, fontsize=18)
        ax.set_xlabel("Time Interval (s)", fontsize=14)
        ax.set_ylabel(r"Value ($\Delta B$)", fontsize=14)
        ax.set_ylim(0, 1)

        legend_title = "BPM" if hue_var == "bpm" else "Number of robots"
        ax.legend(title=legend_title, loc="upper right")

        plt.tight_layout()
        if show:
            plt.show()
        else:
            plt.close()

        return final_df
    

    def harmonic_agreement_boxplot(
        self,
        base_dir="csv",
        step_size=5000,             # ms
        fixed_params=None,          # es. {"delta": 100, "beats": 4, "num_robots": 32, "scale": "major"}
        title="Harmonic agreement evolution",
        hue_var="bpm",              # "bpm" / "num_robots" / "scale"
        show=True,
        scale_fallback="major",
    ):
        if fixed_params is None:
            fixed_params = {}

        # ----------------------------
        # Folder params parsing (stile tuo)
        # ----------------------------
        def parse_folder_params(folder_name: str):
            parts = folder_name.split("_")

            def get_int_after(token):
                return int(parts[parts.index(token) + 1])

            def get_str_after(token):
                return str(parts[parts.index(token) + 1])

            params = {}
            params["bpm"] = get_int_after("BPM") if "BPM" in parts else None
            params["delta"] = get_int_after("delta") if "delta" in parts else None
            params["beats"] = get_int_after("beats") if "beats" in parts else None

            # num_robots: formato ... R_N_32 ...
            params["num_robots"] = None
            if "R" in parts:
                try:
                    i = parts.index("R")
                    if i + 2 < len(parts) and parts[i + 1] == "N":
                        params["num_robots"] = int(parts[i + 2])
                except Exception:
                    pass

            # scale: formato ... scale_major ... oppure scale_pentatonic ...
            params["scale"] = None
            if "scale" in parts:
                try:
                    params["scale"] = get_str_after("scale").strip().lower()
                except Exception:
                    pass

            return params

        # ----------------------------
        # Note -> pitch class (0..11)
        # ----------------------------
        NOTE_RE = re.compile(r"^\s*([A-Ga-g])([#b]?)(-?\d+)?\s*$")
        NOTE_BASE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

        def note_to_pitch_class(x):
            if pd.isna(x):
                return None

            # numeric MIDI
            if isinstance(x, (int, float)) and float(x).is_integer():
                return int(x) % 12

            s = str(x).strip()

            # MIDI numeric as string
            try:
                v = float(s)
                if v.is_integer():
                    return int(v) % 12
            except Exception:
                pass

            m = NOTE_RE.match(s)
            if not m:
                return None

            letter = m.group(1).upper()
            accidental = m.group(2) or ""
            pc = NOTE_BASE_PC[letter]
            if accidental == "#":
                pc = (pc + 1) % 12
            elif accidental == "b":
                pc = (pc - 1) % 12
            return pc

        # ----------------------------
        # H(t) per bin
        # ----------------------------
        def compute_H_for_bin(bin_df: pd.DataFrame, scale_dict: dict):
            """
            scale_dict: {root: [pc,...]}  (es. SCALE_FAMILIES['major'])
            Strategia: per ogni robot, ultima nota nel bin. Poi:
              H = max_root ( count_in_scale(root) / M )
            """
            if bin_df.empty:
                return None

            bin_df = bin_df.sort_values(["musician", "ms"])
            last_notes = bin_df.groupby("musician", as_index=False).tail(1)

            pcs = last_notes["pc"].dropna().astype(int).tolist()
            M = len(pcs)
            if M == 0:
                return None

            best = 0
            for _, scale_pcs in scale_dict.items():
                sset = set(scale_pcs)
                cnt = sum(1 for pc in pcs if pc in sset)
                if cnt > best:
                    best = cnt

            return best / M

        # ----------------------------
        # Main loop
        # ----------------------------
        all_data = []

        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            music_csv = os.path.join(folder_path, "music.csv")
            if not os.path.exists(music_csv):
                continue

            params = parse_folder_params(folder)

            # scala (famiglia) scelta dalla cartella
            scale_name = (params.get("scale") or "").strip().lower()
            if scale_name not in SCALE_FAMILIES:
                scale_name = scale_fallback
            scale_dict = SCALE_FAMILIES[scale_name]

            # filtra parametri fissi
            skip = False
            for k, v in fixed_params.items():
                if k == "scale":
                    if (params.get("scale") or "").strip().lower() != str(v).strip().lower():
                        skip = True
                        break
                else:
                    if params.get(k) != v:
                        skip = True
                        break
            if skip:
                continue

            try:
                df = pd.read_csv(music_csv, delimiter=";")
                df.columns = [c.strip() for c in df.columns]
            except Exception as e:
                print(f"❌ Errore nel file {music_csv}: {e}")
                continue

            required_cols = {"ms", "musician", "note"}
            if not required_cols.issubset(df.columns):
                print(f"❌ Colonne mancanti in {music_csv}: richieste {required_cols}, trovate {set(df.columns)}")
                continue

            if "simulation number" in df.columns:
                sim_groups = df.groupby("simulation number")
            else:
                sim_groups = [(0, df)]

            for sim_id, sim_df in sim_groups:
                sim_df = sim_df.copy()
                sim_df["pc"] = sim_df["note"].apply(note_to_pitch_class)
                sim_df = sim_df.dropna(subset=["pc"])
                if sim_df.empty:
                    continue

                # bin temporale (time_bin in secondi)
                sim_df["time_bin"] = ((sim_df["ms"] // step_size) * step_size) / 1000.0

                rows = []
                for tbin, bin_df in sim_df.groupby("time_bin"):
                    H = compute_H_for_bin(bin_df, scale_dict)
                    if H is None:
                        continue
                    rows.append({"time_bin": tbin, "H": H})

                if not rows:
                    continue

                h_df = pd.DataFrame(rows)
                h_df["bpm"] = params["bpm"]
                h_df["num_robots"] = params["num_robots"]
                h_df["delta"] = params["delta"]
                h_df["beats"] = params["beats"]
                h_df["scale"] = scale_name
                h_df["simulation number"] = sim_id

                all_data.append(h_df)

        if not all_data:
            print("❌ Nessun dato valido.")
            return None

        final_df = pd.concat(all_data, ignore_index=True)

        # rimuovi righe senza hue_var
        if hue_var not in final_df.columns:
            raise ValueError(f"hue_var='{hue_var}' not found in final_df columns: {list(final_df.columns)}")
        final_df = final_df.dropna(subset=[hue_var])

        # ----------------------------
        # Plot
        # ----------------------------
        fig, ax = plt.subplots(figsize=(16, 6))

        sns.boxplot(
            data=final_df,
            x="time_bin",
            y="H",
            hue=hue_var,
            dodge=True,
            ax=ax
        )

        ax.set_title(title, fontsize=18)
        ax.set_xlabel("Time Interval (s)", fontsize=14)
        ax.set_ylabel("H(t) harmonic agreement", fontsize=14)
        ax.set_ylim(0, 1)

        legend_title = {
            "bpm": "BPM",
            "num_robots": "Number of robots",
            "scale": "Scale family",
        }.get(hue_var, hue_var)

        ax.legend(title=legend_title, loc="upper right")
        plt.tight_layout()

        if show:
            plt.show()
        else:
            plt.close()

        return final_df
     

analyzer = DataAnalyzer()
#analyzer.timbre_trend_across_configs(base_dir="csv", step_size=30000)
"""
analyzer.beat_synchrony_boxplot_by_bpm(
    fixed_params={"delta": 100, "beats": 4, "bpm": 60},
    hue_var="num_robots",
    title="Beat synchrony evolution (BPM=60, δ=100)"
)



analyzer.harmonic_agreement_boxplot(
    base_dir="csv",
    hue_var="num_robots",
    fixed_params={
        "delta": 100,
        "beats": 4,
        "bpm": 30,
        "scale": "major",
    },
    title="Harmonic agreement vs number of robots"
)


analyzer.harmonic_agreement_boxplot(
    base_dir="csv",
    hue_var="scale",
    fixed_params={
        "bpm": 60,
        "beats": 4,
        "delta": 100,
        "num_robots": 16,
    },
    title="Harmonic agreement vs scale family",
)
"""

analyzer.harmonic_agreement_boxplot(
    base_dir="csv",
    hue_var="beats",   # confronto 4 vs 5 vs 7
    fixed_params={"bpm": 60, "delta": 100, "num_robots": 16, "scale": "major"},
    step_size=5000,
    title="H(t) vs time (seconds) for different beats"
)

















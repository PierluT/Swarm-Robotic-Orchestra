import numpy as np
import matplotlib.pyplot as plt

# Parametri del modello
N = 10  # Numero di individui
M = 3  # Numero di task
T = 1000  # Numero di iterazioni

alpha = 10  # Rinforzo positivo per chi fa il task
beta = 3    # Rinforzo negativo per chi NON fa il task
phi = 3  # Efficienza del lavoro

# Distribuzione target (60%-20%-20%)
target_distribution = np.array([0.6, 0.2, 0.2])  

# Inizializzazione delle soglie a 500
thresholds = np.full((N, M), 500, dtype=float)

# Stimoli iniziali
stimuli = np.ones(M) * 100

# Storico per la visualizzazione
stimuli_history = np.zeros((T, M))
threshold_history = np.zeros((T, N, M))
tasks_performed_history = np.zeros((T, M))

# Simulazione
for t in range(T):
    task_performed = np.zeros((N, M))

    for i in range(N):
        chosen_task = None
        for j in range(M):
            prob = stimuli[j] ** 2 / (stimuli[j] ** 2 + thresholds[i, j] ** 2)
            if np.random.rand() < prob:
                task_performed[i, j] = 1
                chosen_task = j  

        # Aggiorna le soglie: abbassa quella del task eseguito, aumenta le altre
        if chosen_task is not None:
            thresholds[i, chosen_task] = max(10, thresholds[i, chosen_task] - alpha)
            for other_task in range(M):
                if other_task != chosen_task:
                    thresholds[i, other_task] = min(1000, thresholds[i, other_task] + beta)

    # Distribuzione attuale
    current_distribution = np.sum(task_performed, axis=0) / np.sum(task_performed) if np.sum(task_performed) > 0 else np.zeros(M)
    
    # Modifica dinamica degli stimoli in base alla differenza con la distribuzione target
    delta_stimuli = (target_distribution - current_distribution) * 2  # Il fattore 2 amplifica la correzione
    stimuli += delta_stimuli
    stimuli = np.clip(stimuli, 0, 1000)

    # Salva la storia per analisi
    stimuli_history[t] = stimuli
    threshold_history[t] = thresholds
    tasks_performed_history[t] = np.sum(task_performed, axis=0)

# 📊 PLOT EVOLUZIONE STIMOLI
plt.figure(figsize=(10, 5))
for j in range(M):
    plt.plot(stimuli_history[:, j], label=f'Stimolo {j+1}')
plt.xlabel("Tempo")
plt.ylabel("Intensità dello stimolo")
plt.title("Evoluzione degli stimoli nel tempo")
plt.legend()
plt.show()

# 📊 PLOT EVOLUZIONE THRESHOLDS
plt.figure(figsize=(10, 5))
plt.plot(np.mean(threshold_history, axis=(1,2)), label="Media Thresholds")
plt.plot(np.mean(stimuli_history, axis=1), label="Media Stimoli")
plt.xlabel("Tempo")
plt.ylabel("Valore Medio")
plt.title("Andamento Medio di Stimoli e Soglie")
plt.legend()
plt.show()

# 📊 PLOT TASK ESEGUITI NEL TEMPO
plt.figure(figsize=(10, 5))
for j in range(M):
    plt.plot(tasks_performed_history[:, j], label=f'Task {j+1}')
plt.xlabel("Tempo")
plt.ylabel("Numero di volte eseguito")
plt.title("Numero di volte che ogni task è stato eseguito nel tempo")
plt.legend()
plt.show()

# 📊 CONFRONTO DISTRIBUZIONE DESIDERATA VS EFFETTIVA
total_tasks = np.sum(tasks_performed_history, axis=0)
actual_distribution = total_tasks / np.sum(total_tasks)

labels = [f"Task {i+1}" for i in range(M)]
x = np.arange(M)

plt.figure(figsize=(8, 5))
plt.bar(x - 0.2, target_distribution, width=0.4, label="Distribuzione Desiderata", alpha=0.7)
plt.bar(x + 0.2, actual_distribution, width=0.4, label="Distribuzione Effettiva", alpha=0.7)

plt.xticks(x, labels)
plt.ylabel("Percentuale di esecuzione")
plt.title("Confronto tra Distribuzione Desiderata ed Effettiva")
plt.legend()
plt.show()

# 📌 STAMPA RISULTATI
print("Distribuzione desiderata:", target_distribution)
print("Distribuzione effettiva:", actual_distribution)



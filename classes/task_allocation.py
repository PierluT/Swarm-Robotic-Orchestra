import numpy as np
import matplotlib.pyplot as plt

# Parametri del modello
N = 30  # Numero di individui
M = 3  # Numero di task
T = 1000  # Numero di iterazioni

alpha = 10  # Rinforzo positivo per chi fa il task
beta = 3    # Rinforzo negativo per chi NON fa il task
p = 0.2  # Probabilità di smettere di eseguire un task
delta = 1  # Incremento dello stimolo quando il task non è svolto
phi = 3  # Efficienza del lavoro
t = 1

# Inizializzazione delle soglie a 500 come nel grafico 1a
thresholds = np.full((N, M), 500, dtype=float)

# Intensità degli stimoli iniziale
stimuli = np.ones(M) * 100
# Storico degli stimoli per la visualizzazione
stimuli_history = np.zeros((T, M))
# Storico delle soglie per la visualizzazione
threshold_history = np.zeros((T, N, M))
tasks_performed_history = np.zeros((T, M))
# Simulazione
for t in range(T):
    task_performed = np.zeros((N, M))
    for i in range(N):
        chosen_task = None  # Ogni individuo dovrebbe preferire un solo task
        for j in range(M):
            prob = stimuli[j] ** 2 / (stimuli[j] ** 2 + thresholds[i, j] ** 2)
            if np.random.rand() < prob:
                task_performed[i, j] = 1
                chosen_task = j  # Memorizza il task eseguito
        
        # Aggiorna le soglie: abbassa solo quella del task eseguito, aumenta tutte le altre
        if chosen_task is not None:
            thresholds[i, chosen_task] = max(10, thresholds[i, chosen_task] - alpha)
            for other_task in range(M):
                if other_task != chosen_task:
                    thresholds[i, other_task] = min(1000, thresholds[i, other_task] + beta)
    
        # Aggiornamento dello stimolo: aumenta se pochi fanno il task
    stimuli += delta - (phi/ N) * np.sum(task_performed, axis=0)
    
    stimuli = np.clip(stimuli, 0, 1000)  # Evita stimoli negativi e crescita illimitata
    
    stimuli_history[t] = stimuli
    # Salvataggio della storia delle soglie
    threshold_history[t] = thresholds
    tasks_performed_history[t] = np.sum(task_performed, axis=0)

#print(tasks_performed_history)

# PLOT DELL'ANDAMENTO DEGLI STIMOLI 
plt.figure(figsize=(10, 5))
for j in range(M):
    plt.plot(stimuli_history[:, j], label=f'Stimolo {j+1}')

plt.xlabel("Tempo")
plt.ylabel("Intensità dello stimolo")
plt.title("Evoluzione degli stimoli nel tempo")
plt.legend()
plt.show()

# thresholds plot
plt.figure(figsize=(10, 5))
for i in range(N):
    for j in range(M):
        plt.plot(threshold_history[:, i, j], label=f'Indiv {i+1} - Task {j+1}')

    plt.xlabel("Tempo")
    plt.ylabel("Soglia di risposta")
    plt.title("Evoluzione delle soglie di risposta nel tempo con 3 task")
    plt.legend()
    plt.show()

# 🔹 PLOT DEI TASK ESEGUITI 🔹
plt.figure(figsize=(10, 5))
for j in range(M):
    plt.plot(tasks_performed_history[:, j], label=f'Task {j+1}')

plt.xlabel("Tempo")
plt.ylabel("Numero di volte eseguito")
plt.title("Numero di volte che ogni task è stato eseguito nel tempo")
plt.legend()
plt.show()
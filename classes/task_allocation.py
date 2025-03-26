import numpy as np
import matplotlib.pyplot as plt

# Parametri del modello
N = 20  # Numero di individui
M = 3  # Numero di task
T = 1000  # Numero di iterazioni

alpha = 10  # Rinforzo positivo per chi fa il task
beta = 3    # Rinforzo negativo per chi NON fa il task
p = 0.2  # Probabilità di smettere di eseguire un task
lambda_stimulus = 16  # Incremento dello stimolo quando il task non è svolto
phi = 2  # Efficienza del lavoro

# Inizializzazione delle soglie a 500 come nel grafico 1a
thresholds = np.full((N, M), 500, dtype=float)

# Intensità degli stimoli iniziale
stimuli = np.ones(M) * 100

# Storico delle soglie per la visualizzazione
threshold_history = np.zeros((T, N, M))

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
    stimuli += lambda_stimulus - phi * np.sum(task_performed, axis=0)
    stimuli = np.clip(stimuli, 0, 1000)  # Evita stimoli negativi e crescita illimitata
    
    # Salvataggio della storia delle soglie
    threshold_history[t] = thresholds
"""
# Visualizzazione dei risultati per replicare il comportamento atteso
plt.figure(figsize=(10, 5))
for i in range(N):
    for j in range(M):
        plt.plot(threshold_history[:, i, j], label=f'Indiv {i+1} - Task {j+1}')

    plt.xlabel("Tempo")
    plt.ylabel("Soglia di risposta")
    plt.title("Evoluzione delle soglie di risposta nel tempo con 3 task")
    plt.legend()
    plt.show()
"""
# Ora aggiungiamo il grafico a colonna per l'ultimo task eseguito

# Consideriamo l'ultimo task eseguito da ciascun individuo all'iterazione T-1
last_task_performed = np.argmax(task_performed, axis=1)  # Indica l'indice del task eseguito

# Conta quante persone hanno eseguito ciascun task nell'ultimo step
task_counts = np.bincount(last_task_performed, minlength=M)

# Creiamo il grafico a colonna
plt.figure(figsize=(8, 6))
plt.bar(range(M), task_counts, tick_label=[f'Task {j+1}' for j in range(M)])
plt.xlabel('Task')
plt.ylabel('Numero di individui')
plt.title('Numero di individui che hanno eseguito ciascun task (ultimo step)')
plt.show()

import numpy as np
import matplotlib.pyplot as plt

# Parametri del modello
N = 10  # Numero di individui
M = 3  # Numero di task
T = 3000  # Numero di iterazioni

alpha = 10  # Rinforzo positivo per chi fa il task
beta = 3    # Rinforzo negativo per chi NON fa il task
p = 0.2  # Probabilità di smettere di eseguire un task
lambda_stimulus = 5  # Incremento dello stimolo quando il task non è svolto
phi = 2  # Efficienza del lavoro

# Inizializzazione delle soglie
thresholds = np.full((N, M), 500, dtype=float)

# Intensità degli stimoli iniziale
stimuli = np.ones(M) * 100

# Storico delle soglie
threshold_history = np.zeros((T, N, M))

# Inizializziamo una lista per tracciare l'ultimo task scelto da ogni individuo
last_chosen_task = np.full(N, -1)  # -1 indica che non ha ancora scelto un task

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
        
        # Se l'individuo ha scelto un task, aggiorniamo il suo ultimo task eseguito
        if chosen_task is not None:
            last_chosen_task[i] = chosen_task  # Salviamo il task scelto
        
        # Aggiorna le soglie
        if chosen_task is not None:
            thresholds[i, chosen_task] = max(10, thresholds[i, chosen_task] - alpha)
            for other_task in range(M):
                if other_task != chosen_task:
                    thresholds[i, other_task] = min(1000, thresholds[i, other_task] + beta)
    
    # Aggiornamento dello stimolo
    stimuli += lambda_stimulus - phi * np.sum(task_performed, axis=0)
    stimuli = np.clip(stimuli, 0, 1000)
    
    # Salvataggio della storia delle soglie
    threshold_history[t] = thresholds

# Stampa solo per l'ultima iterazione, assegnando il task precedente se necessario
for i in range(N):
    task_chosen = False  # Flag per verificare se l'individuo ha scelto un task
    for j in range(M):
        if task_performed[i, j] == 1:
            print(f"Individuo {i+1} ha scelto il task {j+1} nell'ultima iterazione (iterazione {T})")
            task_chosen = True
    
    # Se l'individuo non ha scelto alcun task, ripete l'ultimo task scelto
    if not task_chosen:
        if last_chosen_task[i] != -1:  # Se aveva scelto un task in passato
            print(f"Individuo {i+1} non ha scelto un task nell'ultima iterazione, quindi ripete il task {last_chosen_task[i]+1}")
        else:
            print(f"Individuo {i+1} non ha mai scelto un task e rimane inattivo.")

print(task_performed)
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

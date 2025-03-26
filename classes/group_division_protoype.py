import numpy as np
import matplotlib.pyplot as plt

# Parametri della simulazione
N = 10  # Numero di individui
m = 3  # Numero di compiti
T = 2000  # Tempo totale della simulazione
alpha = 3  # Tasso di apprendimento
beta = 1  # Tasso di dimenticanza
dt = 1  # Passo temporale
sigma = 0.5  # Intensità del rumore stocastico
stimulus_growth = 0.2  # Tasso di crescita dello stimolo se il compito non viene svolto
stimulus_decrease = 1.0  # Lo stimolo cala se il task viene eseguito
theta_min = 100  # Soglia minima
theta_max = 1000  # Soglia massima

# Inizializzazione casuale delle soglie per diversificare le scelte iniziali
thresholds = np.random.uniform(400, 600, (N, m, T))

# Stimolo iniziale uguale per tutti i task
s = np.array([0.2, 0.2, 0.2])

# Configurazione desiderata: 60% Task 1, 20% Task 2, 20% Task 3
desired_distribution = np.array([0.6, 0.2, 0.2])

# Funzione per calcolare la probabilità di eseguire un task
def compute_probability(s_j, theta_ij):
    return (s_j ** 2) / (s_j ** 2 + theta_ij ** 2)

# Simulazione della dinamica delle soglie con più task
def update_thresholds(thresholds, s):
    task_choices = np.zeros((N, T), dtype=int)  # Salva il task scelto da ogni individuo nel tempo
    
    for t in range(1, T):
        # Calcola la distribuzione attuale
        current_distribution = np.bincount(task_choices[:, t-1], minlength=m) / N  

        # Aggiorna gli stimoli con un meccanismo di feedback
        for j in range(m):
            error = desired_distribution[j] - current_distribution[j]
            s[j] += stimulus_growth * (1 + error * 5)  # Aumenta lo stimolo se il task è sottorappresentato
        
        for i in range(N):
            probabilities = np.array([compute_probability(s[j], thresholds[i, j, t-1]) for j in range(m)])
            probabilities /= np.sum(probabilities)  # Normalizza le probabilità
            task_selected = np.random.choice(np.arange(m), p=probabilities)  # Scelta probabilistica
            task_choices[i, t] = task_selected  # Salva la scelta del task

            for j in range(m):
                if j == task_selected:
                    correction_factor = 1 - (current_distribution[j] / desired_distribution[j])  
                    thresholds[i, j, t] = thresholds[i, j, t-1] - alpha * dt * correction_factor + np.random.normal(0, sigma)
                else:
                    correction_factor = (desired_distribution[j] / (current_distribution[j] + 1e-6))  
                    thresholds[i, j, t] = thresholds[i, j, t-1] + beta * dt * correction_factor + np.random.normal(0, sigma)

                # Vincolare le soglie tra theta_min e theta_max
                thresholds[i, j, t] = np.clip(thresholds[i, j, t], theta_min, theta_max)

    return thresholds, task_choices

# Esegui la simulazione
thresholds, task_choices = update_thresholds(thresholds, s)

# Conta il numero di individui assegnati a ciascun task alla fine della simulazione
final_task_counts = np.zeros(m, dtype=int)

for i in range(N):
    chosen_task = task_choices[i, -1]  # Ultima scelta registrata
    final_task_counts[chosen_task] += 1

# Confronta la distribuzione ottenuta con quella desiderata
final_distribution = final_task_counts / N
print("Distribuzione finale desiderata:", desired_distribution)
print("Distribuzione finale ottenuta:", final_distribution)

"""
# Plot dell'evoluzione delle soglie per ogni individuo
for i in range(N):
    plt.figure(figsize=(10, 6))
    for j in range(m):
        linestyle = ['-', '--', ':'][j % 3]  # Differenzia i task
        plt.plot(range(T), thresholds[i, j, :], linestyle, label=f'Task {j+1}')
    
    # Personalizza il grafico per ogni individuo
    plt.xlabel("Tempo")
    plt.ylabel("Soglia di risposta")
    plt.title(f"Evoluzione delle soglie - Individuo {i+1}")
    plt.legend()
    plt.show()
"""
# Visualizza la distribuzione finale con un grafico a barre
plt.figure(figsize=(8, 5))
plt.bar(range(1, m+1), final_task_counts, tick_label=[f"Task {j+1}" for j in range(m)], color=['blue', 'orange', 'green'])
plt.xlabel("Task")
plt.ylabel("Numero di individui")
plt.title("Distribuzione finale degli individui tra i task")
plt.show()

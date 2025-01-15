import os

# Ottieni il percorso della cartella dove si trova il file corrente
current_file_directory = os.path.dirname(os.path.abspath(__file__))

print(" current directory " + current_file_directory)
samples_name = "samples"
samples_directory = os.path.join(current_file_directory,samples_name)
if os.path.exists(samples_directory):
    print(f"La path '{samples_directory}' esiste.")
else:
    print(f"La path '{samples_directory}' non esiste.")
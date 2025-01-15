import os
import shutil
from pathlib import Path

# Ottieni la directory del file corrente
current_file_directory = Path(__file__).parent

print(current_file_directory)
png_path = os.path.join(current_file_directory, 'prova')

if os.path.exists(png_path):
    print(f"La path '{png_path}' esiste.")
    # Cancella il contenuto della cartella
    for filename in os.listdir(png_path):
        file_path = os.path.join(png_path, filename)
        try:
            # Rimuovi file o directory
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Rimuove file o link simbolici
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Rimuove directory
            print(f"Rimosso: {file_path}")
        except Exception as e:
            print(f"Errore eliminando {file_path}: {e}")


else:
    print(f"La path '{png_path}' non esiste.")

    
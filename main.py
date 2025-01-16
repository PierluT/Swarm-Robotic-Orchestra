import csv
import argparse
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage

# I pass parameters in the main, as f.ex number of simulations.           
def main():
    parser = argparse.ArgumentParser(description=" Esempio di script con un intero e due booleani")
    parser.add_argument("int_param", type=int, help="Un parametro intero.")
    parser.add_argument("bool_param1", type=lambda x: x.lower() in ("true", "1", "yes"), help="Il primo booleano (true/false).")
    parser.add_argument("bool_param2", type=lambda x: x.lower() in ("true", "1", "yes"), help="Il secondo booleano (true/false).")
    
    # Parsing dei parametri
    args = parser.parse_args()

    # Associa i valori a variabili
    int_param = args.int_param
    bool_video = args.bool_param1
    bool_audio = args.bool_param2  
    # intializations
    supervisor = Supervisor([])
    midi_class = MIDIMessage()
    arena = Arena()
    arena.clear_png_folder()

    # I create a new csv file.
    csv_video_file_name = "video_maker.csv"
    csv_directory = "csv"
    csv_path = supervisor.setup_csv_directory(csv_directory, csv_video_file_name)

    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        # add note infos
        writer.writerow(["simulation number","ms", "robot number", "x", "y","compass", "phase", "colour", "status", "midinote", "pitch", "timbre", "delay"])
        # Ciclo per eseguire le simulazioni
        for simulation_number in range(1, int_param + 1):
            print(f"Esecuzione simulazione {simulation_number}...")
            supervisor.setup_robots()
            for millisecond in range(0,5000):
                for robot in supervisor.dictionary_of_robots:
                    robot.update_phase(millisecond, simulation_number)
                            
                    # COMMUNICATION every 80 ms.   
                    if (millisecond % 80 == 0):
                        supervisor.post_office(robot)
                            
                    # ROBOT STEP
                    if (millisecond % 40 == 0):
                        #  KNOWLEDGE PART
                        distances_to_check = supervisor.make_matrix_control(robot)
                        robot.get_note_info()
                        robot.get_phase_info()
                        # ACTION PART
                        robot.move_robot(distances_to_check)

                        if robot.local_music_map:
                            robot.update_note()
                                
                        if robot.local_phase_map:
                            robot.update_phase_kuramoto_model()
                            
                        robot.clean_buffers()
                                
                        arena.write_robot_data(writer,simulation_number, millisecond, robot)    
            
            arena.load_robot_data(csv_path, simulation_number)
            arena.draw_all_robots()
            supervisor.build_conductor_spartito()
            #print("  ##################     ")
            #print(supervisor.conductor_spartito)
            midi_class.write_csv(supervisor.conductor_spartito,csv_directory)
            supervisor.dictionary_of_robots.clear()
            #supervisor.conductor_spartito.clear()
            # return the paths of the wav files that i need
            wav_files_list = midi_class.finding_wav_from_csv()
            midi_class.generate_audio_from_csv(wav_files_list)
            arena.create_video(output_path= "video_simulation.mp4",audio_path = "final_output.wav", fps = 25, auto_open= True)




if __name__ == "__main__":
        
        main()

"""""
affinity_matrix = supervisor.calculate_instrument_affinity()

    # Visualizza la matrice di affinità
    for instrument1, instrument_dict in affinity_matrix.items():
        print(f"{instrument1}:")
        for instrument2, affinity in instrument_dict.items():
            print(f"  {instrument2}: {affinity:.2f}")
"""





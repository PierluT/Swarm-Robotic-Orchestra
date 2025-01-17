import csv
import argparse
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage

# I pass parameters in the main, as f.ex number of simulations.           
def main():
    parser = argparse.ArgumentParser(description=" Esempio di script con un intero e due booleani")
    parser.add_argument("int_param", type=int, help="Un parametro intero.")
    parser.add_argument("bool_param1", type=lambda x: x.lower() in ("true", "1", "yes"), help="boolean video and audio (true/false).")
    
    # Parsing dei parametri
    args = parser.parse_args()

    # Associa i valori a variabili
    int_param = args.int_param
    bool_video_audio = args.bool_param1 
    
    # intializations
    supervisor = Supervisor([])
    midi_class = MIDIMessage()
    arena = Arena()
    
    csv_path = supervisor.set_up_csv_directory()
    supervisor.clean_csv_directory()
    
    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        # add note infos
        writer.writerow(["simulation number","ms", "robot number", "x", "y","compass", "phase", "colour","midinote", "pitch", "timbre", "delay"])
        # Ciclo per eseguire le simulazioni
        for simulation_number in range(int_param):
            
            print(f"Esecuzione simulazione {simulation_number}...")
            # CLEAN EVERYTHING BEFORE EXECUTION 
            # method to clean previous png files in order to not overlap them.
            arena.clean_png_folder()
            # the method cleans previous csv files and folder and return the path where to write csv files. 
            
            # method to set robot positions and initial random notes.
            supervisor.setup_robots()
            
            for millisecond in range(0,360):
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
                              
                        arena.write_robot_data(writer, simulation_number, millisecond, robot) 
            
            
            supervisor.build_conductor_spartito()
            midi_class.write_csv(supervisor.conductor_spartito)
            supervisor.dictionary_of_robots.clear()
            supervisor.conductor_spartito.clear()
    
    if bool_video_audio: 
        # readers must be outside writer!!       
        arena.load_robot_data(csv_path, simulation_number)
        arena.draw_all_robots()
        wav_files_list = midi_class.finding_wav_from_csv()
        midi_class.generate_audio_from_csv(wav_files_list)
        # video generation audio included
        arena.create_video(output_path= "video_simulation.mp4", audio_path = "final_output.wav", fps = 25, auto_open= True)

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





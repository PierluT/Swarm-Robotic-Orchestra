import csv
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage
from classes.analyzer import DataAnalyzer

# I pass parameters in the main.           
def main():
    parser = argparse.ArgumentParser(description =" Esempio di script con un intero e due booleani")
    parser.add_argument("int_param", type=int, help = "Un parametro intero.")
    parser.add_argument("bool_param1", type=lambda x: x.lower() in ("true", "1", "yes"), help ="boolean video and audio (true/false).")
    
    # Parsing dei parametri
    args = parser.parse_args()
    int_param = args.int_param
    bool_video_audio = args.bool_param1 

    # Controllo della condizione
    if int_param > 1 and bool_video_audio:
        print("Errore: se il parametro intero è maggiore di 1, il booleano deve essere False.")
        sys.exit(1)  # Terminare il programma con codice di errore 1

    print(f"Parametri accettati: int_param={int_param}, bool_video_audio={bool_video_audio}")

    # intializations
    supervisor = Supervisor([])
    midi_class = MIDIMessage()
    arena = Arena()
    analyzer = DataAnalyzer()
    csv_path = supervisor.set_up_csv_directory(int_param)
    
    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["simulation number","ms","robot number","x", "y","compass","beat phase","beat counter","dynamic", "colour","midinote", "pitch", "timbre", "delay"," playing flag"])
        for simulation_number in range(int_param):
            print("##################################")
            print(f"EXECUTION NUMBER {simulation_number}")
            # CLEAN EVERYTHING BEFORE EXECUTION 
            # method to clean previous png files in order to not overlap them.
            arena.clean_png_folder()
            # method to set robot positions and initial random notes.
            supervisor.setup_robots()
            
            for millisecond in range(0,180000):          
                # ROBOTS WRITE A note IN THE GLOBAL SPARTITO
                for robot in supervisor.dictionary_of_robots:
                    # update robot beat phase
                    robot.update_beat_phase(millisecond)
                    
                    # if the robot play then I update the gobal spartito.
                    if robot.playing_flag:
                        # supervisor adds the new robot note line to its global spartito. 
                        supervisor.build_conductor_spartito(robot.my_spartito)
                        supervisor.new_note = True           
                    
                    if (millisecond % 40 == 0): 
                        new_x, new_y, new_vx, new_vy = supervisor.new_positions_control(robot)
                        robot.move_robot(new_x, new_y, new_vx, new_vy)
                        
                        arena.write_robot_data(writer, simulation_number, millisecond, robot)
                    
                
                # SUPERVISOR SIMULATES ROBOT'S EARS SO IT UPDATES ALL OF THEM OF WHAT HAPPENS IN THE ENVIRONMENT.  
                if supervisor.new_note:
                    # I compute the new global stimuli to cominucate to robots.
                    supervisor.update_stimuli()
                    # once I wrote the new notes in the global spartito I share infos to all robots.
                    supervisor.update_global_robot_spartito(millisecond)

                """""
                    # STAMPA DI CONTROLLO
                    print("QUALCUNO HA SUONATO AL ms ", millisecond)
                    print()
                    for robot in supervisor.dictionary_of_robots:
                        print("ROBOT:", robot.number, "global info")
                        for sublist in robot.orchestra_spartito:  # Ogni sublist è una lista di dizionari
                            for entry in sublist:  # Iteriamo sui dizionari dentro la sublist
                                #print(f"ms: {entry['ms']}, musician: {entry['musician']}, dynamic: {entry['dynamic']}")
                                print(entry)
                        print("ultimo ms suonato: ", robot.last_played_ms)
                        print()
               
                    print()
                """
                # I set false for the new cycle.
                supervisor.new_note = False
                # to clean the robot ears.
                supervisor.clean_robot_buffers()
            #for robot in supervisor.dictionary_of_robots:
                #print(robot.stimuli)
            #print(supervisor.conductor_spartito)
            midi_class.write_csv(supervisor.conductor_spartito,simulation_number, csv_path)
            """
            # plot of the timbre threshold evolution
            plt.figure(figsize=(10, 5))
            for robot in supervisor.dictionary_of_robots:
                threshold_history = np.array(robot.timbre_threshold_history)
                for i in range(supervisor.num_timbres):
                    plt.plot(threshold_history[:, i], label=f'Indiv {robot.number + 1} - Task {i+1}')

                plt.xlabel("Tempo")
                plt.ylabel("Soglia di risposta")
                plt.title("Evoluzione delle soglie di risposta nel tempo con 3 task")
                plt.legend()
                plt.show()
            """
            # for another simulation I clear all robot data.
            supervisor.dictionary_of_robots.clear()
            supervisor.conductor_spartito.clear() 
    #ggggggganalyzer.timbre_analysis_distribution(csv_path)
    
    if bool_video_audio: 
        # VISUALIZATION PART       
        arena.load_robot_data(csv_path, simulation_number)
        arena.draw_all_robots()
        wav_files_list = midi_class.finding_wav_from_csv()
        midi_class.generate_audio_from_csv(wav_files_list)
        # video generation audio included
        arena.create_video(output_path= "video_simulation.mp4", audio_path = "final_output.wav", fps = 25, auto_open= True)                           

if __name__ == "__main__":
        main()






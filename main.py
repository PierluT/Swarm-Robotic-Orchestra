import csv
import argparse
import sys
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage
from classes.tempo import TimeSignature


def run_simulation(int_param, bool_video_audio, delta_val, number_of_robots):
    
    print(f"\n--- Simulazione con robot={number_of_robots}, delta={delta_val} ---")
    # initialization
    supervisor = Supervisor(number_of_robots)
    midi_class = MIDIMessage()
    arena = Arena()
    ts = TimeSignature()
    csv_path = supervisor.set_up_csv_directory(int_param, delta_val, ts)
    
    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["simulation number","ms","robot number","x", "y","compass","beat phase","beat counter","dynamic", "colour","midinote", "pitch", "timbre", "delay"," playing flag"])
        for simulation_number in range(int_param):
            print("##################################")
            print(f"EXECUTION NUMBER {simulation_number}")
            # CLEAN EVERYTHING BEFORE EXECUTION 
            arena.clean_png_folder()
            # method to set robot positions and initial random notes.
            supervisor.setup_robots(delta_val, number_of_robots, ts)
            
            for millisecond in range(0,supervisor.time):          
                # ROBOTS WRITE A note IN THE GLOBAL SPARTITO
                for robot in supervisor.dictionary_of_robots:
                    # update robot beat phase
                    robot.update_beat_phase(millisecond)
                    
                    # if the robot play then I update the gobal spartito.
                    if robot.playing_flag:
                        # supervisor adds the new robot note line to its global spartito. 
                        supervisor.build_conductor_spartito(robot.my_spartito)
                        supervisor.new_note = True           
                    
                    # MOVEMENT PART
                    if (millisecond % 40 == 0): 
                        # supervisor controls and manages the new robot positions, in order to
                        # avoid collisions within boundaries and eachother.
                        new_x, new_y, new_vx, new_vy = supervisor.new_positions_control(robot)
                        robot.move_robot(new_x, new_y, new_vx, new_vy)
                        # every 40 ms I write robot data on video.csv
                        arena.write_robot_data(writer, simulation_number, millisecond, robot)
                    
                # SUPERVISOR SIMULATES ROBOT'S EARS SO IT UPDATES ALL OF THEM OF WHAT HAPPENS IN THE ENVIRONMENT.  
                if supervisor.new_note:
                    # once I wrote the new notes in the global spartito I share infos to all robots.
                    supervisor.update_global_robot_spartito(millisecond)
                # I set false for the new cycle.
                supervisor.new_note = False
                # to clean the robot ears.
                supervisor.clean_robot_buffers()
            for robot in supervisor.dictionary_of_robots:
                print("ROBOT:", robot.number, " how many times distribution is correct ", robot.b)
                #robot.print_threshold_history(supervisor.csv_folder_directory)
                robot.print_stimuli_history(supervisor.csv_folder_directory)
            #print(supervisor.conductor_spartito)
            midi_class.write_csv(supervisor.conductor_spartito,simulation_number, csv_path)            
            # for another simulation I clear all robot data.
            supervisor.dictionary_of_robots.clear()
            supervisor.conductor_spartito.clear() 
    #analyzer.timbre_analysis_across_robots(csv_path)
    
    if bool_video_audio: 
        # plot of the timbre threshold evolution.
        # VISUALIZATION PART       
        arena.load_robot_data(csv_path, simulation_number)
        arena.draw_all_robots()
        wav_files_list = midi_class.finding_wav_from_csv()
        midi_class.generate_audio_from_csv(wav_files_list)
        # video generation audio included
        arena.create_video(output_path= "video_simulation.mp4", audio_path = "final_output.wav", fps = 25, auto_open= True)

if __name__ == "__main__":
    
    # Se stai eseguendo il debug, aggiungi i parametri manualmente
    if len(sys.argv) == 1:  # Se non ci sono argomenti da linea di comando
        sys.argv.extend(["1", "false","40", "8"])  # Imposta valori di test
    
    parser = argparse.ArgumentParser()
    parser.add_argument("int_param", type=int, help="Numero di simulazioni")
    parser.add_argument("bool_video_audio", type=lambda x: x.lower() in ("true", "1", "yes"))
    parser.add_argument("delta_val", type=int, help="Valore di delta")
    parser.add_argument("number_of_robots", type=int, help="Numero di robot")
    args = parser.parse_args()

    run_simulation(args.int_param, args.bool_video_audio,args.delta_val, args.number_of_robots)

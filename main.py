import csv
import argparse
import sys
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage
from classes.tempo import TimeSignature

def run_simulation(int_param, bool_video_audio, number_of_robots):
    
    print(f"\n--- Simulazione con robot={number_of_robots}")
    # initialization
    supervisor = Supervisor(number_of_robots)
    midi_class = MIDIMessage()
    arena = Arena()
    ts = TimeSignature()
    csv_path = supervisor.set_up_csv_directory(int_param, ts)
    
    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["simulation number","ms","robot number","status","x", "y","compass","beat phase","beat counter","dynamic", "colour","midinote", "pitch", "timbre", "delay"," playing flag"])
        for simulation_number in range(int_param):
            print("##################################")
            print(f"EXECUTION NUMBER {simulation_number}")
            # CLEAN EVERYTHING BEFORE EXECUTION 
            arena.clean_png_folder()
            # method to set robot positions and initial random notes.
            supervisor.setup_robots(number_of_robots, ts)
            # IMPLEMENTATION OF THE SIMULATION
            for millisecond in range(0,supervisor.time):          
                # ROBOTS WRITE A note IN THE GLOBAL SPARTITO
                for robot in supervisor.dictionary_of_robots:
                        #supervisor.check_robot_status(millisecond, robot)
                        # check if the robot is on or off.
                        if robot.status == "on":
                            # update robot beat phase
                            robot.update_beat_phase(millisecond)
                        
                        # if the robot play then I update the gobal spartito.
                        if robot.playing_flag:
                            # supervisor adds the new robot note line to its global spartito. 
                            supervisor.build_conductor_spartito(robot.my_spartito)
                            supervisor.new_note = True           
                        
                        # MOVEMENT PART
                        if (millisecond % 40 == 0): 
                            if robot.status == "on":
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
            #print(supervisor.conductor_spartito)
            midi_class.write_csv(supervisor.conductor_spartito,simulation_number, csv_path)
            for robot in supervisor.dictionary_of_robots:
                # save png graphs of robot's thresholds
                robot.print_threshold_history(supervisor.csv_folder_directory)
                #  save png files of robot's stimuli history 
                robot.print_stimuli_history(supervisor.csv_folder_directory)   
            # for another simulation I clear all robot data.
            supervisor.dictionary_of_robots.clear()
            supervisor.conductor_spartito.clear() 
    
    if bool_video_audio: 
        # plot of the timbre threshold evolution.
        # VISUALIZATION PART       
        arena.load_robot_data(csv_path, simulation_number)
        arena.draw_all_robots()
        wav_files_list = midi_class.finding_wav_from_csv()
        midi_class.generate_audio_from_csv(wav_files_list)
        # video generation audio included
        arena.create_video(output_path= "video_simulation.mp4", audio_path = "final_output.wav", fps = 25, auto_open= True)
    
    else:
        print("Video and audio generation skipped.")
        

if __name__ == "__main__":
    # if you are doing debug or testing you can set the parameters here.
    if len(sys.argv) == 1:  # if there are no command line arguments
        sys.argv.extend(["1", "true", "8"])  # set up the default values
    
    parser = argparse.ArgumentParser()
    parser.add_argument("int_param", type=int, help="Numero di simulazioni")
    parser.add_argument("bool_video_audio", type=lambda x: x.lower() in ("true", "1", "yes"))
    #parser.add_argument("delta_val", type=int, help="Valore di delta")
    parser.add_argument("number_of_robots", type=int, help="Numero di robot")
    args = parser.parse_args()

    run_simulation(args.int_param, args.bool_video_audio, args.number_of_robots)

import csv
import shutil
import os
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage

# I pass parameters in the main, as f.ex number of simulations.           
def main():

    # intializations
    supervisor = Supervisor([])
    midi_class = MIDIMessage()
    arena = Arena()
    supervisor.setup_robots()
    arena.clear_png_folder()

    # I create a new csv file.
    csv_video_file_name = "video_maker.csv"
    csv_directory = "csv"
    csv_path =supervisor.setup_csv_directory(csv_directory, csv_video_file_name)

    with open(csv_path , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        # add note infos
        writer.writerow(["ms", "robot number", "x", "y","compass", "phase", "colour", "status", "midinote", "pitch", "timbre", "delay"])
                
        for millisecond in range(0,50000):
            for robot in supervisor.dictionary_of_robots:
                robot.update_phase(millisecond)
                        
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
                            
                    arena.write_robot_data(writer,millisecond, robot)    
            
    arena.load_robot_data(csv_path)
    arena.draw_all_robots()
    supervisor.build_conductor_spartito()
    midi_class.write_csv(supervisor.conductor_spartito,csv_directory)
    # return the paths of the wav files that i need
    #wav_files_list = midi_class.finding_wav_from_csv()
    #midi_class.generate_audio_from_csv(wav_files_list)
    #arena.create_video(output_path= "video_simulation.mp4",audio_path = "final_output.wav", fps = 25, auto_open= True)




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





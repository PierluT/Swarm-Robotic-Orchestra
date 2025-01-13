import csv

from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.MIDIMessage import MIDIMessage
            
def main():
    # intializations
    supervisor = Supervisor([])
    midi_class = MIDIMessage()
    arena = Arena()
    supervisor.setup_robots()
    # I create a new csv file.
    video_csv_file  = "video_maker.csv"
    
    with open(video_csv_file , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["ms", "robot number", "x", "y","compass", "phase", "colour", "status"])
        
        for millisecond in range(0,50000):
            for robot in supervisor.dictionary_of_robots:
                robot.update_phase(millisecond)
                
                # COMMUNICATION every 80 ms.   
                if (millisecond % 80 == 0):
                    supervisor.post_office(robot)
                
                # ROBOT STEP
                if (millisecond % 40 == 0):
                    #  KNOWLEDGE PART
                    # can stay here
                    distances_to_check = supervisor.make_matrix_control(robot)
                    # rename methods as : get____info
                    # 1) get info for distances to check ( sensor simulation )
                    # 2) get info for update local music map, change name method with get
                    robot.update_local_music_map()
                    # robot.get_window_info()
                    # 3) get phase info
                    # after processing, clean buffers.
                    # ACTION PART
                    # Now that I have all the info I can act, decide what to do:
                    # 1) distances: decide where to move
                    robot.move_robot(distances_to_check)
                    # SPLIT the moment when you get info and the moment when you USE the infos.
                    
                    
                    if robot.local_music_map:
                        robot.update_note()
                    # if you have phase info apply kuramoto. take out kuramoto from update and put it in this if
                    # if you have something in window list, update.
                    
                    arena.write_robot_data(writer,millisecond, robot)
                

            for robot in supervisor.dictionary_of_robots:
                 robot.clean_music_buffer()
    
    arena.load_robot_data(video_csv_file)
    arena.draw_all_robots()
    supervisor.build_conductor_spartito()
    midi_class.write_csv(supervisor.conductor_spartito)
    midi_class.generate_audio_from_csv()
    arena.create_video(output_path= "video_simulation.mp4",audio_path = "final_output.wav", fps = 25, auto_open= True)

if __name__ == "__main__":
        
        main()







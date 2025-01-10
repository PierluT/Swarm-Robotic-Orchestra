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
        for millisecond in range(0,500000):             
            for robot in supervisor.dictionary_of_robots:
                robot.update_phase(millisecond)
            
                # PHYSICAL SIMULATION
                if (millisecond % 40 == 0):
                    # new positions for everybody by supervisor

                    # I comupte distances of everyone 
                    # the supervisor
                    distances_to_check = supervisor.make_matrix_control() 

                    #supervisor.print_distance_matrix()
                    robot.move_robot(distances_to_check)
                    # I write the infos. 
                    arena.write_robot_data(writer,millisecond, robot)
    
                # LOGICAL SIMULATION   
                if (millisecond % 80 == 0):
                    supervisor.post_office() 
    
    arena.load_robot_data(video_csv_file)
    arena.draw_all_robots()
    supervisor.build_conductor_spartito()
    #midi_class.write_csv(supervisor.conductor_spartito)
    #midi_class.generate_audio_from_csv()
    #arena.create_video(output_path= "video_simulation.mp4", fps = 20)

if __name__ == "__main__":
        
        main()
"""""
             for r in supervisor.dictionary_of_robots:
         print("mappa note robot n.: "+ str(r.number))
         print(r.local_music_map)
         print("ultima nota suonata: "+ str(r.note.midinote))
         print()















        ########## OLD MAIN ###################
         
         # Scrivi i dati in un file CSV
    with open(video_csv_file , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["ms", "robot number", "x", "y","compass", "phase", "colour", "status"])
        global_time = 0
        for millisecond in range(0,60000,supervisor.time_step):             
            for robot in supervisor.dictionary_of_robots:
                # PRIMA SUPERVISOR POI STEP DI ROBOT !!!!!   
                supervisor.collision_and_message_control(robot)
                robot.step(global_time)
                # I write the infos. 
                arena.write_robot_data(writer,millisecond, robot)
            
            global_time += supervisor.time_step  
            for robot in supervisor.dictionary_of_robots:
                 robot.clean_music_buffer()
"""
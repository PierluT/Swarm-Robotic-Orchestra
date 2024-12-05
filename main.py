import csv
import time

from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.tempo import Grammar_Sequence, metronome_grammar,ex_i_grammar
from classes.MIDIMessage import MIDIMessage
            
def main():

    supervisor = Supervisor([])
    # method to create a complete dictionary of robots.
    supervisor.create_dictionary_of_robots()
    # method to compute initial positions in order to avoid overlap.
    supervisor.compute_initial_positions()
    #print(supervisor.dictionary_of_robots)

    # number of measures in the composition
    num_bars_per_composition = 4
    START_SEQUENCE=["M",]*num_bars_per_composition
    G = Grammar_Sequence(ex_i_grammar) 
    final_sequence, seqs = G.create_sequence(START_SEQUENCE)
    # divides notes duration per measure.
    G.dividi_sequenza_ritmica_melodia(final_sequence)   
    midi_class = MIDIMessage()
    # I create a new csv file.
    video_csv_file  = "video_maker.csv"
    
    # Scrivi i dati in un file CSV
    with open(video_csv_file , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["ms", "robot number", "x", "y","compass", "phase", "colour", "status", "is playing"])
        total_time = 0
        step_count = 0
        # the step depends on how much fast arena.draw() can draw.
        for millisecond in range(0,54000,30):             
            for robot in supervisor.dictionary_of_robots: 
                supervisor.collision_and_message_control(robot)
                robot.step()
                # I write the infos. 
                writer.writerow([
                millisecond, 
                robot.number, 
                robot.x, 
                robot.y,
                robot.compass, 
                robot.phase, 
                robot.colour,
                robot.moving_status,
                robot.playing_flag
            ])       
    # test Arena csv reader.
    arena = Arena()
    # I read the csv and draw the sequence.
    #arena.print_robot_data()
    #start = time.perf_counter()
    arena.load_robot_data(video_csv_file)
    
    arena.draw_all_robots()
    #end = time.perf_counter()
    #print(f"Tempo impiegato per visualizzazione finestra: {end - start} secondi")
    #midi_class.midi_event(video_csv_file)
    arena.create_video(output_path= "video_simulation.mp4", fps = 30)

if __name__ == "__main__":
        
        main()

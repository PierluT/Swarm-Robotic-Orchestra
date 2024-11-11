import csv
import time
from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.tempo import Grammar_Sequence, metronome_grammar,ex_i_grammar
            
def main():
    arena = Arena()
    supervisor = Supervisor([])
    # method to create a complete dictionary of robots.
    supervisor.create_dictionary_of_robots()
    supervisor.compute_initial_positions()
    print(supervisor.dictionary_of_robots)
    # method to compute initial positions in order to avoid overlap.
    # dictionary_of_positions = supervisor.compute_initial_positions()
    

    # number of measures in the composition
    num_bars_per_composition = 4
    START_SEQUENCE=["M",]*num_bars_per_composition
    G = Grammar_Sequence(ex_i_grammar) 
    final_sequence, seqs = G.create_sequence(START_SEQUENCE)
    # divides notes duration per measure.
    G.dividi_sequenza_ritmica_melodia(final_sequence)
    
    # I create a new csv file.
    video_csv_file  = "video_maker.csv"

    # Scrivi i dati in un file CSV
    with open(video_csv_file , mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["millisecond", "robot number", "x", "y", "phase", "colour", "is playing"])
        for millisecond in range(0,4001,1000):    
            for robot in supervisor.dictionary_of_robots:
                writer.writerow([
                millisecond, 
                robot.number, 
                robot.x, 
                robot.y, 
                robot.phase, 
                robot.colour,
                robot.playing_flag
            ])
                robot.step()
                supervisor.collision_and_message_control(robot)
        time.sleep(1)
    
    print(f"File '{video_csv_file }' creato con successo.")



if __name__ == "__main__":
        main()

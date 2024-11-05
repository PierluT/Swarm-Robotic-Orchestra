from classes.supervisor import Supervisor
from classes.arena import Arena
from classes.tempo import Grammar_Sequence, metronome_grammar,ex_i_grammar
            
def main():
    arena = Arena()
    supervisor = Supervisor([])
    # method to create a complete dictionary of robots.
    supervisor.create_dictionary_of_robots()
    # method to compute initial positions in order to avoid overlap.
    supervisor.compute_initial_positions() 
    # number of measures in the composition
    num_bars_per_composition = 4
    START_SEQUENCE=["M",]*num_bars_per_composition
    G = Grammar_Sequence(ex_i_grammar) 
    final_sequence, seqs = G.create_sequence(START_SEQUENCE)
    # divides notes duration per measure.
    G.dividi_sequenza_ritmica_melodia(final_sequence)
    # HOW LONG IS IT? could be around 4 seconds. This tempo should be reached by consensous because each robot could have different freq. clocks.
    while True:       
        arena.arena.fill(0)
        for n in supervisor.dictionary_of_robots:
            n.step()
            # method to check collision and message exchanges.
            supervisor.collision_and_message_control(n)
            arena.draw_robot(n)
        arena.show_arena()
        #supervisor.print_half_matrix()

if __name__ == "__main__":
        main()

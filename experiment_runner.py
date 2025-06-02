import configparser
import itertools
import argparse
from main import run_simulation

def main():

    parser = argparse.ArgumentParser(description="Batch di simulazioni con vari parametri.")
    parser.add_argument("int_param", type=int, help="Numero di simulazioni per combinazione")
    parser.add_argument("bool_video_audio", type=lambda x: x.lower() in ("true", "1", "yes"))
    args = parser.parse_args()

    # Definisci i range di parametri da testare
    number_of_robots = [20]
    delta_vals = [30]

    param_combinations = list(itertools.product(number_of_robots, delta_vals))
    print(f"\n>> Avvio batch: {len(param_combinations)} combinazioni × {args.int_param} simulazioni")

    for idx, (number_of_robots,delta) in enumerate(param_combinations):
        print(f"\n▶ Combinazione {idx + 1}: robots={number_of_robots}, delta={delta}")
        
        run_simulation(
            int_param=args.int_param,
            bool_video_audio=args.bool_video_audio,
            delta_val=delta,
            number_of_robots = number_of_robots
        )

if __name__ == "__main__":
    main()
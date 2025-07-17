import math
import random
import time
import os
import shutil
from classes.robot import Robot
from classes.tempo import TimeSignature
from classes.dictionaries import orchestra_to_midi_range
from collections import defaultdict
from configparser import ConfigParser

config = ConfigParser()
config.read('configuration.ini')

class Supervisor:
    
    def __init__(self, number_of_robots):
        self.csv_folder_directory = ""
        # boundaries of rectangle area
        self.rectangleArea_width = int(config['PARAMETERS']['width_arena'])
        self.rectangleArea_heigth = int(config['PARAMETERS']['height_arena'])
        self.time = int(config['PARAMETERS']['milliseconds'])
        self.min_off_duartion = 1000
        #self.delta_incidence = values_dictionary['delta_incidence']
        self.arena_area = self.rectangleArea_width * self.rectangleArea_heigth
        # number of robots in the arena
        self.number_of_robots = number_of_robots
        # dictionary of created robots
        self.dictionary_of_robots = []
        # value for collision
        self.collision_margin = int(config['PARAMETERS']['radar'])
        # dictionary of distance bewteen a robot and each others.
        self.distances = [[0 for _ in range(self.number_of_robots)] for _ in range(self.number_of_robots)] 
        # final music sheet that will be converted into audio file.
        self.conductor_spartito = []
        # to found the minimum a maximum mid value.
        self.min_midinote = 0
        self.max_midinote = 0
        # to estimate phases convergence
        self.target_precision = 0.01
        # this value is the ability of a robot to see thing around it.
        self.sensor = int(config['PARAMETERS']['sensor'])
        self.initial_bpm = int(config['PARAMETERS']['bpm'])
        self.csv_folder = ""
        self.new_note = False
        # TIMBRE MODULE
        # stimuli parameters
        self.stimuli_update_mode = config['PARAMETERS']['stimuli_update']
        self.timbre_dictionary = orchestra_to_midi_range
        self.num_timbres = sum(len(instruments) for instruments in self.timbre_dictionary.values())
    
    # method to compute iteratively the min and max midinote value that robot can play.
    def compute_midi_range_values(self):
        min_value = float('inf')  
        max_value = float('-inf') 
        for section in orchestra_to_midi_range.values():
            for instrument_range in section.values():
                min_value = min(min_value, min(instrument_range))
                max_value = max(max_value, max(instrument_range))
        self.min_midinote = min_value
        self.max_midinote = max_value 
        
        return self.min_midinote, self.max_midinote
    
    def setup_robots(self, delta_val, number_of_robots, ts):
        # I associate a note and a timbre for each robot.
        self.create_dictionary_of_robots(delta_val, number_of_robots, ts)
        # I set the initial positions of the robots.
        self.compute_initial_positions()
    
    def set_up_csv_directory(self,simulation_number,delta_val, ts):
        s_n = simulation_number
        #distribution_type = "_target_distribution" if self.stimuli_update_mode == "delta" else "_standard_distribution"
        minutes = int(self.time / 60000)
        csv_directory = "csv"
        
        csv_folder = (
            # number of simulations
            f"S_N_{s_n}"
            # number of robots
            f"_R_N_{self.number_of_robots}"
            # bpm of the simulation
            f"_BPM_{self.initial_bpm}"
            # minutes of the simulation
            f"_min_{minutes}"
            # delta value to study
            f"_delta_{delta_val}"
            # number of beats in the measure
            f"_beats_{ts.denominator_time_signature[0]}"
        )
        # to set up the general directory of the csv files.
        self.csv_folder_directory = os.path.join(csv_directory, csv_folder)
        csv_video_file_name = "video.csv"
        csv_music_file_name = "music.csv"
        
        if not os.path.exists(csv_directory):
            # creates directory if doesn't exist.
            os.mkdir(csv_directory)  
        csv_folder_directory = os.path.join(csv_directory,csv_folder)
        if not os.path.exists(csv_folder_directory):
            # creates directory if doesn't exist.
            os.mkdir(csv_folder_directory)  
        
        csv_final_path = os.path.join(csv_folder_directory,csv_video_file_name)
        # Percorso file music.csv
        csv_music_path = os.path.join(csv_folder_directory, csv_music_file_name)
        # Svuota il file music.csv se esiste
        if os.path.exists(csv_music_path):
            os.remove(csv_music_path) 
        
        return csv_final_path
    
    # method to clean previous files and csv folders. 
    def clean_csv_directory(self):
        # remove all the files contained in the directory.
        for file_name in os.listdir(self.csv_folder):
            file_path = os.path.join(self.csv_folder, file_name)
            try:
                if os.path.isfile(file_path):  
                    os.remove(file_path)
                elif os.path.isdir(file_path):  
                    shutil.rmtree(file_path)
            except Exception as e:
                    print(f"Errore durante la rimozione del file {file_path}: {e}")
        print(f"Tutti i file nella cartella {self.csv_folder} sono stati eliminati.")       

    def compute_phase_bar_value(self, ts):
        seconds_in_a_beat = 60 / self.initial_bpm
        
        number_of_beats, denominator = ts.time_signature_combiantion
        phase_bar_value = 1000 * (seconds_in_a_beat * number_of_beats)
        # By now I set the notes length as the beat seoconds duration. Then
        # I will have to change with the possible length available durations.
        return number_of_beats, phase_bar_value, seconds_in_a_beat, ts.time_signature_combiantion

    # method to return the list of robots and assign a phase to each of them.
    def create_dictionary_of_robots(self,delta_val, number_of_robots, ts): 
         
        # TIME SIGNATURE SETUP.
        number_of_beats, phase_bar_value, seconds_in_a_beat, t_s = self.compute_phase_bar_value(ts)
        beats_array = list(range(1, number_of_beats +1))
        for n in range(self.number_of_robots):
            # to set the initial status of the robots.
            #status = random.choice(["on", "off"])
            status = "on"
            # I create a new robot with the initial parameters.
            robot = Robot(number = n, phase_period = phase_bar_value, delay_values = beats_array,
                           sb = seconds_in_a_beat, time_signature = t_s,
                           delta_val = delta_val, total_robots = number_of_robots,
                            status = status)
            robot.compute_beat_threshold()
            robot.choose_timbre()
            # I set the initial random note as one the notes that the initial timbre can play.
            notes_range = robot.get_midi_range_from_timbre()
            # robot.min_midinote, robot.max_midinote = self.compute_midi_range_values()
            initial_random_note = random.choice(notes_range)
            robot.create_new_note(initial_random_note, bpm = self.initial_bpm, duration = seconds_in_a_beat)
            robot.set_dynamic()
            # the supervisor has a complete dictionary of all the robots.
            self.dictionary_of_robots.append(robot)

    def check_robots_status(self, millisecond):
        """Check the status of each robot and update their status if necessary."""
        for robot in self.dictionary_of_robots:
            if robot.status == "off":
                # Check if the off duration has passed
                if millisecond >= robot.off_start_time + robot.off_duration:
                    # Set the robot to "on" after the off duration
                    robot.status = "on"
                    robot.off_start_time = None
                    robot.on_start_time = millisecond
                    robot.on_duration = 60000
            elif robot.status == "on":
                # Check if the on duration has passed
                if millisecond >= robot.on_start_time + robot.on_duration:
                    # Set the robot to "off" after the on duration
                    robot.status = "off"
                    robot.on_start_time = None
                    robot.off_start_time = millisecond
                    robot.off_duration = 60000
                    # Set a new off duration for the next cycle
                    #robot.off_duration = random.randint(self.min_off_duartion, self.time)

    # method to set the intial positions of the robots, in order to avoid overlap.
    def compute_initial_positions(self):
        margin = 10
        valid_initial_positions = []
        initial_robot = self.dictionary_of_robots[0]
        initial_x_robot = initial_robot.compute_initial_x_position()
        initial_y_robot = initial_robot.compute_initial_y_position()
        
        initial_robot.x = initial_x_robot
        initial_robot.y = initial_y_robot
        valid_initial_positions.append(initial_robot)

        for robot_to_check in self.dictionary_of_robots[1:]:
            # Inifinte cycle unitl I found a valid position
            while True:  
                x_position_to_check = robot_to_check.compute_initial_x_position()
                y_position_to_check = robot_to_check.compute_initial_y_position()
                # Flag to control overlaps
                overlap_found = False  
                for valid_robot in valid_initial_positions:
                    distance_between_origins = math.sqrt(pow(valid_robot.x - x_position_to_check, 2) + pow(valid_robot.y - y_position_to_check, 2))
                    distance_between_radars = valid_robot.radius + robot_to_check.radius + margin
                    
                    if distance_between_origins <= distance_between_radars:
                        overlap_found = True  
                        # Break in case overlap found
                        break  

                if not overlap_found:  
                    robot_to_check.x = x_position_to_check
                    robot_to_check.y = y_position_to_check
                    valid_initial_positions.append(robot_to_check)
                    # Break in case valid position found.
                    break

        return valid_initial_positions 
    
    def compute_next_robot_position(self,robot):
        """Compute next possible position of the"""
        next_x = robot.x + robot.vx
        next_y = robot.y + robot.vy
        return next_x, next_y

    def compute_distance_with_coordinates(self, x1, y1, x2, y2):
        """Calcola la distanza tra due punti (centri dei robot)."""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def new_positions_control(self, initial_robot):
        next_x, next_y = self.compute_next_robot_position(initial_robot)
        new_vx, new_vy = initial_robot.vx, initial_robot.vy  # Mantiene la velocità attuale

        # 1️⃣ Controllo dei bordi PRIMA di verificare le collisioni con gli altri robot
        if next_x - initial_robot.radius <= 10 or next_x + initial_robot.radius >= self.rectangleArea_width:
            new_vx = -new_vx  # Inverte la velocità lungo X
            next_x = initial_robot.x + new_vx  # Calcola la nuova posizione

        if next_y - initial_robot.radius <= 10 or next_y + initial_robot.radius >= self.rectangleArea_heigth:
            new_vy = -new_vy  # Inverte la velocità lungo Y
            next_y = initial_robot.y + new_vy  # Calcola la nuova posizione

        # Se dopo la correzione dei bordi non c'è collisione, restituisci i nuovi valori
        collision = False
        for j in range(self.number_of_robots):
            if j != initial_robot.number:
                robot_b = self.dictionary_of_robots[j]
                if self.compute_distance_with_coordinates(next_x, next_y, robot_b.x, robot_b.y) <= 2 * initial_robot.radius + 20:
                    collision = True
                    break
        if not collision:
            return next_x, next_y, new_vx, new_vy  #  Nessuna collisione, il robot può muoversi normalmente

        #  Se invece c'è una collisione con un altro robot, trova una nuova traiettoria
        new_angle = self.find_new_trajectory_angle(initial_robot)
        new_vx = initial_robot.velocity * math.cos(new_angle)
        new_vy = initial_robot.velocity * math.sin(new_angle)
        new_x = initial_robot.x + new_vx
        new_y = initial_robot.y + new_vy

        return new_x, new_y, new_vx, new_vy  # Ritorna i nuovi valori con traiettoria modificata

    def find_new_trajectory_angle(self, robot):
        current_angle = math.atan2(robot.vy, robot.vx)
        step = math.radians(10)  # Angolo di ricerca incrementale
        max_attempts = 36  # Prova fino a coprire 360 gradi
        
        for i in range(max_attempts):
            new_angle = current_angle + (i * step)
            next_x = robot.x + robot.velocity * math.cos(new_angle)
            next_y = robot.y + robot.velocity * math.sin(new_angle)
            
            collision = False
            
            for j in range(self.number_of_robots):
                if j != robot.number:
                    other_robot = self.dictionary_of_robots[j]
                    if self.compute_distance_with_coordinates(next_x, next_y, other_robot.x, other_robot.y) >= 2 * robot.radius:
                        continue
                    collision = True
                    break
            
            if not collision:
                return new_angle  # Restituisce il primo angolo disponibile senza collisioni
        
        return current_angle  # Se non trova alternative, mantiene la direzione attuale

    # EVERY ROBOT UPDATES ITS GLOBAL SPARTITO TO BE CONSCIOUS OF WHAT HAS BEEN PLAYED.
    def update_global_robot_spartito(self, millisecond):
        # I update the global infos of every robot.
        for robot in self.dictionary_of_robots:
            # robot stores what the other ones have been played.
            robot.update_orchestra_spartito(self.conductor_spartito, millisecond)    

    def send_neighborg_positions(self):
        for robot in self.dictionary_of_robots.values():
            robot.neighbors = []  # Resetta la lista dei vicini per evitare duplicati
            for other_robot in self.dictionary_of_robots.values():
                if robot.number != other_robot.number:  # Escludi se stesso
                    robot.neighbors.append((other_robot.x, other_robot.y))

    def clean_robot_buffers(self):
        for robot in self.dictionary_of_robots:
            robot.clean_buffers() 

    # method to send and receive messages.
    def post_office(self,initial_robot):
        initial_robot.set_emitter_message()
        for j in range(initial_robot.number +1, len(self.distances)):
            #distance_to_check = self.distances[initial_robot.number][j]
            # block to handle phase communication between robots.
            #if distance_to_check <= self.threshold:
            robot1_chat = self.dictionary_of_robots[initial_robot.number]
            robot2_chat = self.dictionary_of_robots[j]
            self.handle_communication(robot1_chat, robot2_chat)
    
    # method to handle phase communication.
    def handle_communication(self,robot1, robot2):
        robot2.set_emitter_message()
        robot2.recieved_message.append(robot1.forwarded_message.copy())
        robot1.recieved_message.append(robot2.forwarded_message.copy())

    # method to update robot positions
    def update_positions(self,initial_robot):
        initial_robot.x += initial_robot.vx
        initial_robot.y += initial_robot.vy
        
    # unifies spartito of all robots and sort them form a crhonological point of view.
    def build_conductor_spartito(self, robot_spartito):
        # adds every element of the robot spartito to the supervisor conductor spartito.
        self.conductor_spartito.extend(robot_spartito)
        # orders the conductor spartito by ms value.
        self.conductor_spartito.sort(key=lambda x: x["ms"])
        return self.conductor_spartito

"""
"""
import math
import numpy as np
import random
import time
import os
import shutil
from classes.robot import Robot
from classes.file_reader import File_Reader
from classes.tempo import TimeSignature
from classes.dictionaries import orchestra_to_midi_range, music_formations
from collections import defaultdict


file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Supervisor:
    
    def __init__(self, robots):
        # boundaries of rectangle area
        self.rectangleArea_width = values_dictionary['width_arena']
        self.rectangleArea_heigth = values_dictionary['height_arena']
        self.arena_area = self.rectangleArea_width * self.rectangleArea_heigth
        # number of robots in the arena
        self.number_of_robots = values_dictionary['robot_number']
        # dictionary of created robots
        self.dictionary_of_robots = []
        # value for communication
        self.threshold = values_dictionary['threshold']
        # value for collision
        self.collision_margin = values_dictionary['radar']
        # dictionary of distance bewteen a robot and each others.
        self.distances = [[0 for _ in range(self.number_of_robots)] for _ in range(self.number_of_robots)] 
        # final music sheet that will be converted into audio file.
        self.conductor_spartito = []
        self.global_spartito = []
        # to found the minimum a maximum mid value.
        self.min_midinote = 0
        self.max_midinote = 0
        # to estimate phases convergence
        self.target_precision = 0.01
        # time interval for phases check 
        self.last_check_time = time.time()
        # this value is the ability of a robot to see thing around it.
        self.sensor = values_dictionary['sensor']
        self.initial_bpm = values_dictionary['bpm']
        self.music_formations = music_formations
        self.csv_folder = ""
        self.new_note = False
        # timbre module
        # Parametri degli stimoli
        self.lambda_stimulus = 5  
        self.phi = 2 
        self.timbre_dictionary = orchestra_to_midi_range
        self.num_timbres = sum(len(instruments) for instruments in self.timbre_dictionary.values())
        self.timbre_list = [instrument for instruments in self.timbre_dictionary.values() for instrument in instruments]
        # I set an array of lenght number of timbres ( as tasks ) with 100 as initial value.
        self.stimuli = np.ones(self.num_timbres) * 100
    
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
    
    def setup_robots(self):
        # I associate a note and a timbre for each robot.
        self.create_dictionary_of_robots()
        # I set the initial positions of the robots.
        self.compute_initial_positions()
    
    def set_up_csv_directory(self,simulation_number):
        s_n = simulation_number
        #csv_file_name = f"s_n{s_n}r_n{self.number_of_robots}_thr{self.threshold}_area{self.arena_area}.csv"
        csv_directory = "csv"
        csv_folder = f"S_N{s_n}R_N{self.number_of_robots}_Thr{self.threshold}_Area{self.arena_area}"
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
            open(csv_music_path, "w").close() 
        
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

    def compute_phase_bar_value(self):
        seconds_in_a_beat = 60 / self.initial_bpm
        ts = TimeSignature()
        number_of_beats, denominator = ts.time_signature_combiantion
        phase_bar_value = 1000 * (seconds_in_a_beat * number_of_beats)
        # By now I set the notes length as the beat seoconds duration. Then
        # I will have to change with the possible length available durations.
        return number_of_beats, phase_bar_value, seconds_in_a_beat, ts.time_signature_combiantion

    # method to return the list of robots and assign a phase to each of them.
    def create_dictionary_of_robots(self):  
        number_of_beats, phase_bar_value, seconds_in_a_beat, t_s = self.compute_phase_bar_value()
        beats_array = list(range(1, number_of_beats +1))
        for n in range(self.number_of_robots):
            robot = Robot(number = n, phase_period = phase_bar_value, delay_values = beats_array, sb = seconds_in_a_beat, time_signature = t_s, neighbors_number = self.number_of_robots)
            robot.compute_beat_threshold()
            # to set the initial random timbre. the first time stimulis is 100 for everyone, so the timbre will be random.
            robot.choose_timbre(self.stimuli)
            chosen_timbre = robot.timbre
            # I set the initial random note as one the notes that the initial timbre can play.
            for family, instruments in self.timbre_dictionary.items():
                if chosen_timbre in instruments:
                    note_range = instruments[chosen_timbre]
                    initial_random_note = random.choice(note_range)
                    break

            robot.create_new_note(initial_random_note, bpm = self.initial_bpm, duration = seconds_in_a_beat)
            robot.set_dynamic()
            #robot.set_timbre_from_midi()
            # the supervisor has a complete dictionary of all the robots.
            self.dictionary_of_robots.append(robot)

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
                    distance_between_radars = valid_robot.radar_radius + robot_to_check.radar_radius + margin
                    
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
    
    # method to compute distances between robots
    def compute_distance(self, robot1, robot2):
        distance = np.sqrt((robot1.x - robot2.x) ** 2 + (robot1.y - robot2.y) ** 2)
        return round(distance)
    
    # Metodo per calcolare e aggiornare la matrice delle distanze
    def make_matrix_control(self, initial_robot):
        
        self.update_positions(initial_robot)
        
        for j in range(initial_robot.number + 1, self.number_of_robots):
                robot_b = self.dictionary_of_robots[j]
                # compute the distance between robots.
                distance_between_robots = self.compute_distance(initial_robot, robot_b)
                # I store only the values that teh robot is able to read.
                if distance_between_robots <= self.sensor:
                    self.distances[initial_robot.number][j] = distance_between_robots
                    self.distances[j][initial_robot.number] = distance_between_robots

        return self.distances 
    
    def compute_task_performed(self):
        """
        Compute task performed base on supervisor conductor spartito.
        Every timbre has 1 if it is recently played, otherwise 0.

        """
        # initialize the array of task performed by the robots.
        task_performed = np.zeros(self.num_timbres)
        # extract the timbres that have been played from the conductor spartito.
        played_timbres = [entry['timbre'] for entry in self.conductor_spartito]
        # controls if the timbre has been played.
        for i, timbre in enumerate(self.timbre_list):
            if timbre in played_timbres:
                task_performed[i] = 1

        return task_performed

    def update_stimuli(self):
        # I compute the timbres perfromed by the robots to compute what is needed to be played.
        task_performed = self.compute_task_performed()
        # apply the stimuli update formula form the paper.
        self.stimuli += self.lambda_stimulus - self.phi * np.sum(task_performed, axis=0)
        self.stimuli = np.clip(self.stimuli, 0, 1000)

    # EVERY ROBOT UPDATES ITS GLOBAL SPARTITO TO BE CONSCIOUS OF WHAT HAS BEEN PLAYED.
    def update_global_robot_spartito(self, millisecond):
        # I compute the new global stimuli to cominucate to robtos..
        self.update_stimuli()
        # I update the global infos of every robot.
        for robot in self.dictionary_of_robots:
            # robot stores what the other ones have been played.
            robot.update_orchestra_spartito(self.conductor_spartito)    
            # with the stored info, robot applies kuramoto model on its phase.
            robot.update_phase_kuramoto_model(millisecond)
            # TIMBRE MODULE
            robot.choose_timbre(self.stimuli)
        
        # once coordinated phase, robot applies beat synchronization.
        for robot in self.dictionary_of_robots:     
            robot.update_beat_firefly(millisecond)

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

    # method to print distances between robots.
    def print_distance_matrix(self):

        print("Matrice delle distanze:")
        # Stampa l'intestazione della matrice (numeri dei robot)
        header = "     " + " ".join(f"{i:6}" for i in range(len(self.distances)))
        print(header)
        print("-" * len(header))

        # Stampa ogni riga con il numero del robot come intestazione
        for i, row in enumerate(self.distances):
            row_data = " ".join(f"{distance:6.2f}" for distance in row)
            print(f"{i:3} | {row_data}")

    # method to check periodically if phases are converging or not.
    def check_phases_convergence(self):
        # current time for phases check
        current_time = time.time()
        # I print matrix every 4 seconds.
        if current_time - self.last_check_time >= 0.5:
            # Update time from the last control. 
            self.last_check_time = current_time
            robot_phases = (np.array([robot.phase for robot in self.dictionary_of_robots]))
            print(robot_phases)
            # compute mean of phases and verify if the phases are near to that value.
            mean_phase = np.mean(robot_phases)
            phase_diff = np.abs(robot_phases - mean_phase)
            converging = np.all(phase_diff < self.target_precision)
            # Print if phases are converging or not.
            print("Fasi attuali:",robot_phases)
            if converging:
                print("Le fasi stanno convergendo.")
            else:
                print("Le fasi non stanno convergendo.")
            
            return converging
        return None  
        
    # unifies spartito of all robots and sort them form a crhonological point of view.
    def build_conductor_spartito(self, robot_spartito):
        # adds every element of the robot spartito to the supervisor conductor spartito.
        self.conductor_spartito.extend(robot_spartito)
        # orders the conductor spartito by ms value.
        self.conductor_spartito.sort(key=lambda x: x["ms"])

        return self.conductor_spartito

    def calculate_instrument_affinity(self):
        affinity_dict = defaultdict(lambda: defaultdict(int))
        instrument_count = defaultdict(int)
        for formation, instruments in music_formations.items():
            for instrument in instruments:
                instrument_count[instrument] += 1
            # Compute affinity for every instrument that appears in the fomration dictionary.
            for i in range(len(instruments)):
                for j in range(i + 1, len(instruments)):
                    instrument1 = instruments[i]
                    instrument2 = instruments[j]
                    affinity_dict[instrument1][instrument2] += 1
                    affinity_dict[instrument2][instrument1] += 1  
        affinity_matrix = {}
        for instrument1, instrument_dict in affinity_dict.items():
            affinity_matrix[instrument1] = {}
            total_pairs = len(music_formations)  
            for instrument2, count in instrument_dict.items():
                affinity_matrix[instrument1][instrument2] = count / total_pairs
    
        return affinity_matrix

"""""
    # Metodo per calcolare e aggiornare la matrice delle distanze
    def make_matrix_control(self, initial_robot):
        
        self.update_positions(initial_robot)
        
        for j in range(initial_robot.number + 1, self.number_of_robots):
                robot_b = self.dictionary_of_robots[j]
                # compute the distance between robots.
                distance_between_robots = self.compute_distance(initial_robot, robot_b)
                # I store only the values that teh robot is able to read.
                if distance_between_robots <= self.sensor:
                    self.distances[initial_robot.number][j] = distance_between_robots
                    self.distances[j][initial_robot.number] = distance_between_robots

        return self.distances
    
    # method to update robot positions
    def update_positions(self,initial_robot):
        initial_robot.x += initial_robot.vx
        initial_robot.y += initial_robot.vy
        

"""
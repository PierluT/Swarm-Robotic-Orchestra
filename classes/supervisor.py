import math
import numpy as np
import random
import time
from classes.robot import Robot
from classes.file_reader import File_Reader


file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Supervisor:
    
    def __init__(self, robots):
        # boundaries of rectangle area
        self.rectangleArea_width = values_dictionary['width_arena']
        self.rectangleArea_heigth = values_dictionary['height_arena']
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
        # to have clock for comunications already happened and avoid infite message exchange.
        self.clock_interval_dictionary = {}
        # to have clock for notes comunications already happened and avoid infite message exchange.
        self.clock_interval_notes_dictionary = {}
        # value to control that phase message exchanges doesn't happens cpuntinously.
        self.comuncation_clock_interval = values_dictionary['comunication_clock_interval']
        # value to relate phase update and robot steps.
        self.time_step = values_dictionary['time_step']
        # value to control that notes message exchanges doesn't happen cpuntinously. 
        # final music sheet that will be converted into audio file.
        self.conductor_spartito = []
        # to estimate phases convergence
        self.target_precision = 0.01
        # time interval for phases check 
        self.last_check_time = time.time()
    

    # method to return the list of robots and assign a phase to each of them.
    def create_dictionary_of_robots(self):      
        for n in range(self.number_of_robots):
            robot = Robot(number = n)
            robot.create_new_note(random.randint(0,11))
            #robot.set_note()
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
                
                #print("x random da validare: " + str(x_position_to_check) + " y random da validare: " + str(y_position_to_check))
                # Flag to control overlaps
                overlap_found = False  
                for valid_robot in valid_initial_positions:
                    distance_between_origins = math.sqrt(pow(valid_robot.x - x_position_to_check, 2) + pow(valid_robot.y - y_position_to_check, 2))
                    distance_between_radars = valid_robot.radar_radius + robot_to_check.radar_radius + margin
                    
                    if distance_between_origins <= distance_between_radars:
                        overlap_found = True  
                        #print("coordinata x sbagliata: " + str(x_position_to_check) + " coordinata y sbagliata: " + str(y_position_to_check))
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
    
    # x il futuro un buffer solo.
    # un metodo solo con un paramtero 
    
    # method to handle phase communication
    def handle_communication(self,robot1, robot2):
        # I create a unique key to control the message exchange between a pair of robots.
        pair_key = tuple(sorted((robot1.number, robot2.number)))      
        current_time = time.time()
        # ADD A MAXIMUM OF ROBOTS TO REACH.
        # for the first time iteraction.
        if pair_key not in self.clock_interval_dictionary:
            self.clock_interval_dictionary[pair_key] = 0
        # If the 0.10 seconds interval is finished.
        if current_time - self.clock_interval_dictionary[pair_key] >= float(self.comuncation_clock_interval):
            robot1.set_emitter_message()
            robot2.set_emitter_message()
            robot2.recieved_message = robot1.forwarded_message
            robot1.recieved_message = robot2.forwarded_message
            # update interval value
            self.clock_interval_dictionary[pair_key] = current_time
        
        # method for music messages.
        self.music_communication(robot1,robot2)

    def music_communication(self,robot1, robot2):
        # MUSIC MESSAGES EXCHANGE
        # I creat a tuple to not replicate the messages exchange.
        pair_key_notes = tuple(sorted((robot1.number, robot2.number)))
        current_note_time = time.time()
        # for the first time interaction
        if pair_key_notes not in self.clock_interval_notes_dictionary:
            self.clock_interval_notes_dictionary[pair_key_notes] = 0
        # if the time note communication interval is finished.
        #if current_note_time - self.clock_interval_notes_dictionary[pair_key_notes] >= float(self.note_communication_interval):
        robot1.set_musical_message()
        robot2.set_musical_message()
        robot2.recieved_note = robot1.forwarded_note
        robot1.recieved_note = robot2.forwarded_note
            # update interval value
            #self.clock_interval_notes_dictionary[pair_key_notes] = current_note_time

    # method to print distances between robots.
    def print_distances_dictionary(self):
        for pair, distance in self.distances.items():
            print(f"{pair} : {distance}")
        print()

    # method to check distan
    def make_matrix_control(self,initial_robot):  
        # Compute distances between robot in input and all the others
        for j in range(len(self.dictionary_of_robots)):
            if j == initial_robot.number:
                continue  # If is itself
            robot_to_check = self.dictionary_of_robots[j]            
            # compute distances
            distance_between_robots = self.compute_distance(initial_robot, robot_to_check)            
            # Update distances dictionary in a symmetric way.
            self.distances[initial_robot.number][robot_to_check.number] = distance_between_robots

            # collision control
            if distance_between_robots < (2*self.collision_margin) + 10:
                initial_robot.change_direction_x_axes()
                robot_to_check.change_direction_y_axes()
    
    # method to send and receive messages.
    # DIFFERENTIATE LOGIC AND PYSICS, so handle differently collision and 
    def post_office(self,initial_robot):
        for j in range(initial_robot.number +1, len(self.distances)):
            distance_to_check = self.distances[initial_robot.number][j]
            
            # block to handle phase communication between robots.
            if distance_to_check <= self.threshold:              
                robot1_chat = self.dictionary_of_robots[initial_robot.number]
                robot2_chat = self.dictionary_of_robots[j]
                #print("robot numero: "+ str(robot1_chat.number)+ " robot numero: "+ str(robot2_chat.number)+ " threshold")
                self.handle_communication(robot1_chat, robot2_chat)
  
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
        return None  # Nessun controllo effettuato
    
    
    def collision_and_message_control(self,robot_to_parse):
        self.make_matrix_control(robot_to_parse)
        #for i in range(self.time_step):
        # every 2 steps. a parameter that you can study.
        #self.post_office(robot_to_parse)
        #self.check_phases_convergence()
    
    def nearest_timestep(self,ms):
        """Round value to the nearest ms considering the step interval."""
        return round(ms / self.time_step) * self.time_step
        
    # unifies spartito of all robots and sort them form a crhonological point of view.
    def build_conductor_spartito(self):
        self.conductor_spartito = []
        for robot in self.dictionary_of_robots:
            
            adjusted_spartito = [
            
            {**entry, "ms": self.nearest_timestep(entry["ms"])}
            for entry in robot.my_spartito
        ]
            # Extend the full spartito with the player ones.
            self.conductor_spartito.extend(adjusted_spartito)
        # I sort the final music sheet considering ms.
        self.conductor_spartito.sort(key=lambda x: x["ms"])
        
        #print(self.conductor_spartito)
    

"""""
    def print_half_matrix(self):
        robot_indexes = []
        for i in self.dictionary_of_robots:
            robot_indexes.append(i.number)
            # Stampa gli indici delle colonne
        print("     ", end='')  # Spazio iniziale per l'intestazione
        for index in robot_indexes:
            print(f"{index:<5}", end=' ')
        print()  # Nuova riga dopo l'intestazione

        # Stampa la matrice solo per la parte superiore
        for i in range(len(self.distances)):
            print(f"{robot_indexes[i]:<5}", end=' ')  # Indice del robot
            for j in range(len(self.distances[i])):
                if j > i:  # Stampa solo la parte superiore
                    print(f"{self.distances[i][j]:<5}", end=' ')
                else:
                    print("     ", end=' ')  # Spazio vuoto per la parte inferiore
            print()  # Nuova riga dopo ogni riga della matrice 

        # MUSIC MESSAGES EXCHANGE
        pair_key_notes = tuple(sorted((robot1.number, robot2.number)))
        current_note_time = time.time()
        # for the first time interaction
        if pair_key_notes not in self.clock_interval_notes_dictionary:
            self.clock_interval_notes_dictionary[pair_key_notes] = 0
        # if the time note communication interval is finished.
        #if current_note_time - self.clock_interval_notes_dictionary[pair_key_notes] >= float(self.note_communication_interval):
        robot1.set_musical_message()
        robot2.set_musical_message()
        robot2.recieved_note = robot1.forwarded_note
        robot1.recieved_note = robot2.forwarded_note
        robot1.update_local_music_map()
        robot2.update_local_music_map()
            #robot1.clean_music_buffer()
            #robot2.clean_music_buffer()

"""


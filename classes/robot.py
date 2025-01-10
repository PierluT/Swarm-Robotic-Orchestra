import math
import numpy as np
import time
import random
import datetime
from collections import defaultdict, deque
from classes.file_reader import File_Reader
from classes.dictionaries import colours,major_scales
from classes.tempo import Note

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Robot:
    
    def __init__(self,number):
        self.number = number
        self.radius = values_dictionary['radius']
        self.rectangleArea_width = values_dictionary['width_arena']
        self.rectangleArea_heigth = values_dictionary['height_arena']
        self.radar_radius = values_dictionary['radar']
        self.N = values_dictionary['robot_number']
        self.colour = colours['green']
        self.velocity = float(values_dictionary['velocity'])
        self.vx = random.choice([-1, 1]) * self.velocity
        self.vy = random.choice([-1, 1]) * self.velocity
        # initial position for the robot
        self.x = 0
        self.y = 0
        # value to show robot orientation.
        self.compass = ((0, 0), (0, 0))
        # variables form module 1
        self.phase = np.random.uniform(0, 2 * np.pi)
        self.clock_frequency = 0.25
        self.K = 1
        self.T = datetime.timedelta(seconds=4)
        # buffers for incoming and emmiting messages. 
        self.recieved_message = []
        self.forwarded_message = []
        # buffers for notes
        self.recieved_note = []
        self.forwarded_note = []
        # time step for phase communication.
        self.time_step = values_dictionary['time_step']
        # flags for controlling the moment to play.
        self.playing_flag = False
        self.triggered_playing_flag = False
        self.last_direction_change_time = time.time()
        # moving status
        self.moving_status = ""
        self.stop_counter = 0
        self.moving_counter = 0
        # MUSIC VARIABLES
        self.scales = major_scales
        self.note = ""
        #self.id_note_counter = 0
        self.max_music_neighbourgs = 6
        self.max_notes_per_neighbourg = 1
        # variable to control the previous midinote I played
        self.previous_midinote = 0
        # variable to control if in the previous iteraction I play in a common scale with neirghbourgs.
        self.harmony = False
        self.scale_name = None
        self.probable_scales = []
        self.flag_included_proper_midinote = False
        self.my_spartito = []
        self.local_music_map = defaultdict(list) 
        self.interval_pattern = [2, 2, 1, 2, 2, 2, 1]

    def __repr__(self):
        return f"Robot(number = {self.number}, coordinate x = {self.x}, y = {self.y}, phase = {self.phase})"
    
    def set_moving_status(self,status):
        self.moving_status = status
    
    def moving_status_selection(self):
        rnd = random.random()
        # %50 to move
        if rnd < 0.55:
            action = "move"
            
        # %75 to stop
        elif rnd < 0.45:
            action = "stop"
            # Reset the counter when robot stops.
            self.pause_counter = 0
        # 
        else:
            action = "rotate"
        
        self.set_moving_status(action)
        return action
    
    def compute_initial_x_position(self):
        possible_x_coordinate = random.randint(int(self.radar_radius + 10), int(self.rectangleArea_width - self.radar_radius - 10))
        return possible_x_coordinate
    
    def compute_initial_y_position(self):  
        possible_y_coordinate = random.randint(int(self.radar_radius + 10), int(self.rectangleArea_heigth - self.radar_radius - 10))
        return possible_y_coordinate

    def compute_robot_compass(self):
        magnitude = math.sqrt(self.vx**2 + self.vy**2)
        end_x = int(self.x)  # Valore di default
        end_y = int(self.y)

        if magnitude == 0:
            self.vx = random.choice([-1, 1]) * self.velocity  # Imposta una velocità casuale
            self.vy = random.choice([-1, 1]) * self.velocity        
        else:
            direction_x = (self.vx / magnitude) * self.radius
            direction_y = (self.vy / magnitude) * self.radius
            end_x = int(self.x + direction_x)
            end_y = int(self.y + direction_y)
        
        self.compass = ((self.x, self.y), (end_x, end_y))        

    def clean_buffers(self):
        self.forwarded_message.clear()
        self.recieved_message.clear()
    
    def clean_music_buffer(self):
        self.forwarded_note.clear()
        self.recieved_note.clear()
    
    # manage differently the collision
    def change_direction_x_axes(self):
        self.vx = -self.vx
                  
    def change_direction_y_axes(self):
        self.vy = -self.vy 
    
    #return angle direction in rad.
    def get_angle(self):
        return math.atan2(self.vx,self.vy)
    
    def control_robot_movement_from_status(self):
        if self.moving_status == "move":
            if self.moving_counter < 50:
                self.x += self.vx
                self.y += self.vy
                self.moving_counter += 1
        elif self.moving_status == "stop":
            if self.pause_counter < 20:  
               self.x += 0
               self.y += 0
               self.pause_counter += 1   
            
        elif self.moving_status == "rotate":
            self.change_direction()
            #print(" rotation")
        
        # to check boundary collisions.
        if self.x - self.radar_radius <= 10 or self.x + self.radar_radius >= self.rectangleArea_width - 10:
            self.change_direction_x_axes()
        if self.y - self.radar_radius <= 10 or self.y + self.radar_radius >= self.rectangleArea_heigth - 10:
            self.change_direction_y_axes()
    
    def moveRobot(self):
        # Aggiorna la posizione
        self.x += self.vx
        self.y += self.vy
        # Controlla se sono trascorsi 3 secondi dal cambio direzione
        current_time = time.time()
        if current_time - self.last_direction_change_time >= 1:
            self.change_direction()
            self.last_direction_change_time = current_time  # Aggiorna il tempo del cambio di direzione
            #print(f"Robot {self.number} ha cambiato direzione a {current_time}",flush=True)

        # Controlla i bordi per il rimbalzo
        if self.x - self.radar_radius <= 10 or self.x + self.radar_radius >= self.rectangleArea_width - 10:
            self.change_direction_x_axes()
        if self.y - self.radar_radius <= 10 or self.y + self.radar_radius >= self.rectangleArea_heigth - 10:
            self.change_direction_y_axes()
            
    def change_direction(self):
        # Cambia direzione con un angolo casuale
        angle = random.uniform(0, 2 * math.pi)  # Angolo casuale in radianti
        speed = math.sqrt(self.vx**2 + self.vy**2)  # Mantieni la velocità costante
        self.vx = speed * math.cos(angle)  # Nuova componente X
        self.vy = speed * math.sin(angle)  # Nuova componente Y
        self.x += self.vx
        self.y += self.vy    

    def update_note(self):
        # extract only notes from my dictionary
        notes_to_check = [note[0] for note in self.local_music_map.values()]
        #print(notes)
        # I add my note to the array of local music notes.
        #notes_to_check.append(self.note.midinote)
        #print(notes)
        mas = 0
        scale_matches = {}
        for scale_name, scale_notes in self.scales.items():
            matching_notes = [note for note in notes_to_check if note in scale_notes]
            scale_matches[scale_name] = len(matching_notes)

            # found the scale with major number of common notes.
            max_matches = max(scale_matches.values())
            mas = max_matches
            best_scales = [scale_name for scale_name, match_count in scale_matches.items() if match_count == max_matches]
        
        print("number max: "+str(mas)+ " for robot: "+str(self.number))
        # control if my note is included in one of the probable scales:
        for scale in best_scales:
            print("probable scale for r number: "+ str(self.number)+ " "+ str(scale))
            scale_notes = self.scales[scale]
            if self.note.midinote in scale_notes:
                 # put a flag if the note that I play is included in one of the best scales found for the harmony.
                self.flag_included_proper_midinote = True
                print("robot :"+ str(self.number)+ " is already in harmony")
        if not self.flag_included_proper_midinote:
            print("note robot :"+ str(self.number)+" not included in the best scales")
            # function change 70-30 to call it or not.
            #self.change_note(best_scales) 
            
        self.flag_included_proper_midinote = False 
    
    # general method to create note
    def create_new_note(self, midi_value):
        note = Note( midinote = midi_value)
        self.note = note
        # I store the midi
        self.previous_midinote = midi_value

    # mehtod to change the note if I'm not in harmony
    def change_note(self,best_scales):
        change_probability = random.random()
        # I change note
        if change_probability < 0.7:
            print(f"r: {self.number} changes note")
            # I found the closest scale
            closest_scale = min(
                best_scales,
                key=lambda scale_name: min(
                    abs(self.note.midinote - note) if abs(self.note.midinote - note) <= 6 else 12 - abs(self.note.midinote - note)
                    for note in self.scales[scale_name]
                )
            )

            # Trova la nota più vicina nella scala più vicina
            closest_note = min(
                self.scales[closest_scale],
                key=lambda note: min(abs(self.note.midinote - note), 12 - abs(self.note.midinote - note))
            )

            # change note
            self.note.midinote = closest_note
        else: 
            #self.create_new_note(self.previous_midinote)
            print(f"r: {self.number} kept the same note {self.previous_midinote} not in harmony")      

    # method to set the message to send for kuramoto model
    def set_emitter_message(self):
        entry = {
            "robot number": self.number,
            "phase": float(self.phase)
        }
        self.forwarded_message.append(entry)
    
    # metod to set the message to send for harmonic harmonicity.
    def set_musical_message(self):
        entry = {
            "robot number": self.number,
            "note": self.note.midinote
        }
        self.forwarded_note.append(entry)
    
    # Every robot has a dictionary on what is the last note that others are playing.
    # With this structure I can predict the next note to play consulting music scales dictionary.
    # last 4 notes for every of my neighbourghs whom I reach trheshold.
    def update_local_music_map(self):
        # Verifica se ci sono messaggi ricevuti
        if self.recieved_note:
            # Itera su tutte le note ricevute
            for note_list in self.recieved_note:
                if isinstance(note_list, list):  # Verifica che ogni elemento sia una lista
                    for entry in note_list:  # Itera sui dizionari nella lista
                        if isinstance(entry, dict):  # Assicura che l'elemento sia un dizionario
                            robot_number = entry.get("robot number")
                            note = entry.get("note")
                            
                            # Se il robot non è nel dizionario, inizializza una coda per le sue note
                            if robot_number not in self.local_music_map:
                                self.local_music_map[robot_number] = deque(maxlen=self.max_notes_per_neighbourg)

                            # Aggiungi la nuova nota alla coda del robot
                            self.local_music_map[robot_number].append(note)
            
            # Se il dizionario supera il numero massimo di robot, rimuovi il più vecchio
            while len(self.local_music_map) > self.max_music_neighbourgs:
                # Usa `popitem(last=False)` per rimuovere il primo elemento (il più vecchio)
                oldest_robot = next(iter(self.local_music_map))
                del self.local_music_map[oldest_robot]

    # method to print note messages. 
    def print_musical_buffers(self):
        # Controllo e stampa delle recieved notes
        if self.forwarded_note :  # Controlla se il buffer non è vuoto
            print("r: " + str(self.number) + " forwarded note: ")
            for entry in self.forwarded_note:
                print(f"\t Note details: {entry['note'].midinote}")
        # Controllo e stampa delle recieved notes
        if self.recieved_note:  # Controlla se il buffer non è vuoto
            print("r: " + str(self.number) + " recieved note: ")
            for entry in self.recieved_note:
                print(f"\t Note details: {entry['note'].midinote}")
    
    # method to print the internal dictionary of the robot 
    def print_local_music_dictionary(self):
        
        clean_map = {
            # converts deque into list
            robot_id: list(notes)  
            for robot_id, notes in self.local_music_map.items()
        }
        print(f"Robot {self.number} dictionary of others' last played notes: {clean_map}")



    # method to write robot music sheet.
    def add_note_to_spartito(self,ms):
        
        spartito_entry = {
            "ms": ms,
            "musician": self.number,
            "note": self.note.midinote,
            "dur": self.note.dur,
            "amp": self.note.amp,
            "bpm": self.note.bpm
        }

        self.my_spartito.append(spartito_entry)
    
    # method to control that robot enters only the forst time in the playing status.
    def control_playing_flag(self,current_ms):
        if 0 <= self.phase < 1:
            # the first time that I enter means that I have to play.
            if not self.triggered_playing_flag:
                self.playing_flag = True
                self.triggered_playing_flag = True
                self.colour = colours['blue']
                # PROBLEM OF WHEN WRITE THE NOTES TO INDIVIDUAL SPARTITO ( DIFFERENTIATE BETWEEN DECISION AND SUPPOSING NOTES? )
                # that has to be separated by the 0 cross phase.
                #self.create_new_note(random.randint(0,11))
                self.add_note_to_spartito(current_ms)  
            # Means that is not the first time that I enter in the condition, so I have to reset false.
            else:
                self.playing_flag = False
                self.colour = colours['blue']
        # Means that my phase doesn't allow me to play.
        else:
            self.triggered_playing_flag = False
            self.playing_flag = False
            self.colour = colours['green']
    
    # method to update internal robot phase.
    def update_phase(self,global_time,counter):
        current_ms = global_time + counter
        if self.recieved_message:
            #print("r. numero: "+str(self.number)+ " ha ricevuto un messaggio")
            for message in self.recieved_message:
                phase_value = message['phase']
                #print(f"Phase value: {phase_value}")
                self.update_phase_kuramoto_model(phase_value)
            self.clean_buffers()
        self.phase += (2 * np.pi / 4000)
        # normalization only if I reach 2pi then I go to 0.
        self.phase %= (2 * np.pi)
        # method to control if I have the permission to play.
        self.control_playing_flag(current_ms)
        
    # method for kuramoto model
    def update_phase_kuramoto_model(self,recieved_phase):
        self.phase += self.K * np.sin(recieved_phase - self.phase)
        # normalization
        self.phase %= (2 * np.pi) 
         

    # robot updates itself in terms of position and phase.
    def step(self,millisecond):
        self.moving_status_selection()
        self.moveRobot()
        self.update_local_music_map()
        if self.local_music_map:
            self.update_note()
        else:
            print("dizionario vuoto")
        
        for i in range(self.time_step):
            self.update_phase(millisecond,i)
        
        #self.set_note()
        self.compute_robot_compass()
        
"""""
        else:
            # function to set harmony true or false. If all the notes are in one majority scale.
            self.consult_local_music_dictionary()
            #print("r: "+ str(self.number)+ " harmony value "+str(self.harmony))
            #and self.scale_name is not None
            print(self.probable_scales)
            if  self.harmony :
                #print("r: "+ str(self.number) + " "+str(self.harmony))
                # If I already reach harmonicity I play the same note as before.
                self.create_new_note(self.previous_midinote)
                print("r: "+ str(self.number)+ " reached harmony in "+ str(self.scale_name))
                
            # If I don't reach harmony, probability of 70% to change
            change_probability = random.random()  # Numero casuale tra 0 e 1
            if change_probability < 0.7:  
                self.consult_local_music_dictionary()
                print(f"r: {self.number} note changes note")
            else:
                # 30% to mantain the same note
                self.create_new_note(self.previous_midinote)
                print(f"r: {self.number} kept the same note {self.previous_midinote}")

        #self.update_local_music_map()
        #self.clean_music_buffer()
"""
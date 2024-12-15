import math
import numpy as np
import time
import random
import datetime
from classes.file_reader import File_Reader
from classes.dictionaries import colours,major_midi_scales
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
        self.scales = list(major_midi_scales.keys())
        self.note = ""
        self.id_note_counter = 0
        # variable to compute prediciton
        self.my_prediction = ""
        # variable to control the previous midinote I played
        self.previous_midinote = 0
        # variable to control the reach of consensousness
        self.consensous = False
        #self.midinote = 0
        self.my_spartito = []
        self.local_music_map = {}

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
    
    # method to predict the next note to play.
    def set_note(self):
        # if is the first iteraction.
        if self.id_note_counter == 0:
            # I choose a random scale form the scales fo the dictionary
            random_scale_key = random.choice(self.scales)
            print (" scala scelta per robot n.: "+ str(self.number)+ random_scale_key)
            random_scale_notes = major_midi_scales[random_scale_key]
            # I choose a random note from the notes of the previous scale.
            random_note = random.choice(random_scale_notes)
            print (" nota scelta per robot n.: "+ str(self.number)+ str(random_note))
            self.create_new_note(random_note,random_scale_key)
        else:
            self.probablity_note()

    # general method to create note
    def create_new_note(self,midi_value,scale_value):
        note = Note(midinote = midi_value, id = self.id_note_counter)
        self.note = note
        self.previous_midinote = midi_value
        self.id_note_counter += 1
        self.my_prediction = scale_value
        print(self.note)
    
    def probablity_note(self):
        # I enter only if I didn't reach the consensous already.
        if not self.consensous:
           #prob = random.random()
           
           print("robot n. "+ str(self.number) + " non cambia nota")
           self.create_new_note(self.previous_midinote,self.my_prediction)
               
        else:
            print("robot n.: " +str(self.number)+ " consenso ottenuto")
               
    def change_note_by_semitone(self):
        # If I am in the lower boundary I have to add a semitone
        if self.previous_midinote == 60:
            
            new_midinote = self.previous_midinote + 1
            # metodo per predire la nota
        elif self.previous_midinote == 82:
            # If I am in the upper boundary I have to remove  a semitone 
            new_midinote = self.previous_midinote - 1
            # metodo per predire la nota
        
        else:
            # for all other values, the choose is random
            semitone = random.choice([-1, 1])
            #print(type(self.previous_midinote)) 
            #new_midinote = self.previous_midinote + semitone
            # metodo per predire la nota

        # Stampa il nuovo valore per debug
        print(f"Nuovo valore di previous_midinote: " + str(self.previous_midinote))
        return self.previous_midinote
    
    # method to set the message to send for kuramoto model
    def set_emitter_message(self):
        entry = {
            "robot number": self.number,
            "phase": float(self.phase)
        }
        self.forwarded_message.append(entry)
    
    # metod to set the message to send for harmonic consensous.
    def set_musical_message(self):
        entry = {
            "robot number": self.number,
            "note": self.note
        }
        self.forwarded_note.append(entry)
    
    # Every robot has a dictionary on what is the last note that others are playing.
    # With this structure I can predict the next note to play consulting music scales dictionary.
    # last 4 notes for every of my neighbourghs whom I reach trheshold.
    def update_local_music_map(self):
        for entry in self.recieved_note:
            robot_number = entry.get("robot number")
            note = entry.get("note")
            note_id = id(note)

            # Verifica se il robot number è già presente nel dizionario
            if robot_number not in self.local_music_map:
                self.local_music_map[robot_number] = []  # inizializza una lista per il robot

            # Verifica se la nota è già presente (per evitare duplicati della stessa nota)
            if note_id in [id(existing_note) for existing_note in self.local_music_map[robot_number]]:
                continue

            # Aggiungi la nuova nota nella lista del robot
            self.local_music_map[robot_number].append(note)

            # Se la lista contiene più di 4 note, rimuovi la più vecchia
            if len(self.local_music_map[robot_number]) > 4:
                self.local_music_map[robot_number].pop(0)  # rimuove la nota più vecchia

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
    
    def print_local_music_dictionary(self):
        print(f"Robot {self.number} dictionary of others last played notes: {self.local_music_map}")

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
                self.set_note()
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
        for i in range(self.time_step):
            self.update_phase(millisecond,i)
        self.compute_robot_compass()
        
"""""
# method to predict the next note to play.
    def set_note(self):
        # if is the first iteraction.
        if self.id_note_counter == 0:
            # I choose a random scale form the scales fo the dictionary
            random_scale = random.choice(self.scales)
            # I choose a random note from the notes of the previous scale.
            random_note = random.choice(random_scale)
            note = Note(midinote = random_note, id = self.id_note_counter)
            self.note = note
            self.previous_midinote = random_note
            self.id_note_counter += 1
            self.my_prediction = random_scale
        else:
            self.probablity_note()


    if prob < 0.01:
               self.change_note_by_semitone()
               print("robot n. "+ str(self.number) + " cambia nota")
"""
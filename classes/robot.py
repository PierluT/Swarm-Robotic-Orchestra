import math
import numpy as np
import time
import random
import datetime
from collections import deque
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
        self.id_note_counter = 0
        self.max_music_neighbourgs = 4
        self.max_notes_per_neighbourg = 1
        # variable to control the previous midinote I played
        self.previous_midinote = 0
        # variable to control if in the previous iteraction I play in a common scale with neirghbourgs.
        self.harmony = False
        self.scale_name = None
        self.probable_scales = []
        #self.midinote = 0
        self.my_spartito = []
        self.local_music_map = {}
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

    # method to predict the next note to play.
    def set_note(self):
        
        # if is the first iteraction.
        if self.id_note_counter == 0:
            # I choose a random scale form the scales fo the dictionary
            random_scale_key = random.choice(list(self.scales.keys())) 
            random_scale_notes = self.scales[random_scale_key]
            # I choose a random note from the notes of the previous scale.
            random_note = random.choice(random_scale_notes)
            self.create_new_note(random_note)
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

    # general method to create note
    def create_new_note(self, midi_value):
        note = Note( midinote = midi_value)
        self.note = note
        # I store the mdidi
        self.previous_midinote = midi_value
        self.id_note_counter += 1

    def extract_notes_from_local_music_dictionary(self):
        # Lista per raccogliere solo le note
        all_notes = []
        # Estrai solo le note dalla local_music_map
        for robot_id, notes in self.local_music_map.items():
            if notes:  # Verifica che la deque non sia vuota
                note_object = notes[0]  # Accedi al primo (e unico) elemento nella deque
                all_notes.append(note_object.midinote) 

        return all_notes    

    def control_harmony(self):
        # in this case I have to include also the note I'm playing.
        self.probable_scales = self.find_probable_scales(include_current_note=True)
        
        # Se più di una scala contiene tutte le note, non siamo in armonia
        if len(self.probable_scales) == 1:
            self.harmony = True
            self.scale_name = self.probable_scales[0]
        else:
            self.harmony = False
            #self.scale_name = self.probable_scales
            #print(self.probable_scales)
        
        return self.probable_scales

    def consult_local_music_dictionary(self):
        self.probable_scales.clear()
        self.probable_scales = self.find_probable_scales(include_current_note=False)
        #print(self.probable_scales)
        
        if len(self.probable_scales) > 1:
            # if there are many scales with max matches there's an ambigous harmony
            #self.harmony = False
            #self.scale_name = None
            print(f"For robot {self.number},Ambiguous harmony, {len(self.probable_scales)} possible scales.")
            #print( self.probable_scales)
            self.find_discriminative_notes()

        else:
            # if there's only a maximum matching scale, we found harmony.
            self.harmony = True
            self.scale_name = self.probable_scales[0]
            print(f"For robot {self.number}, the majority scale is: {self.scale_name}")
    
        #self.probable_scales.clear()

    # method to consult local dictionary. In the case of choosing the next note I don't need to include the note I'm playing, otherwise in the case that 
    # I have to control harmonicity I have to inclue also my note.
    def find_probable_scales(self, include_current_note=False):
        # Estrai le note dai vicini
        all_notes = self.extract_notes_from_local_music_dictionary()
        
        # Se include_current_note è True, aggiungi la tua nota alla lista
        if include_current_note:
            all_notes.append(self.note.midinote)
        
        # Crea un dizionario per memorizzare il numero di note corrispondenti per ogni scala
        scale_matches = {}
        
        # Itera su tutte le scale e conta le note in comune
        for scale_name, scale_notes in self.scales.items():
            # Conta quante note della tua lista sono nella scala
            matching_notes = [note for note in all_notes if note in scale_notes]
            # Memorizza il numero di note comuni
            scale_matches[scale_name] = len(matching_notes)
        
        # Trova il numero massimo di note in comune
        max_matches = max(scale_matches.values())
        
        # Restituisci tutte le scale che hanno il massimo numero di note comuni
        self.probable_scales = [scale_name for scale_name, matches in scale_matches.items() if matches == max_matches]
        
        return self.probable_scales
    
    # method to find a peculiar note that helps me to discard a possible scale
    def find_discriminative_notes(self):
        discriminative_notes = []
        scale_to_discriminative_note = {}  # Mappa scala -> nota discriminativa

        for i in range(len(self.probable_scales)):
            for j in range(i + 1, len(self.probable_scales)):
                scale1 = self.probable_scales[i]
                scale2 = self.probable_scales[j]
                
                # Trova le note uniche
                unique_to_scale1 = set(self.scales[scale1]) - set(self.scales[scale2])
                unique_to_scale2 = set(self.scales[scale2]) - set(self.scales[scale1])
                
                # Aggiungi alle note discriminative
                discriminative_notes.extend(list(unique_to_scale1))
                discriminative_notes.extend(list(unique_to_scale2))

        # Rimuovi duplicati
        discriminative_notes = list(set(discriminative_notes))

        # Escludi la nota attuale se è presente
        if self.note.midinote in discriminative_notes:
            discriminative_notes.remove(self.note.midinote)
        
        # Verifica ogni nota discriminativa per l'armonia
        valid_scales = []
        for note_to_test in discriminative_notes:
            self.create_new_note(note_to_test)
            self.control_harmony()
            
            # Mappa la scala alla nota discriminativa se l'armonia è valida
            if self.harmony:
                scale_name = self.scale_name  # Scala armoniosa trovata
                scale_to_discriminative_note[scale_name] = note_to_test
                print(f"Discriminative note {note_to_test} found for scale {scale_name}")

        # Scarta le scale non valide
        valid_scales = [scale for scale in self.probable_scales if scale in scale_to_discriminative_note]

        # Aggiorna le scale probabili con solo quelle valide
        self.probable_scales = valid_scales

        if len(self.probable_scales) > 1:
            print(f"Ambiguous harmony, multiple possible scales: {self.probable_scales}")
        else:
            print(f"Harmony found, the valid scale is: {self.probable_scales}")



    # method to get the scale from the name. 
    def get_scale(self, number):
        if number in self.scales:
            return self.scales[number]        

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
            "note": self.note
        }
        self.forwarded_note.append(entry)
    
    # Every robot has a dictionary on what is the last note that others are playing.
    # With this structure I can predict the next note to play consulting music scales dictionary.
    # last 4 notes for every of my neighbourghs whom I reach trheshold.
    def update_local_music_map(self):
        # Verifica se ci sono messaggi ricevuti
        if self.recieved_note:
            # Itera su tutte le note ricevute
            for entry in self.recieved_note:
                robot_number = entry.get("robot number")
                note = entry.get("note")
                
                # Se il robot non è nel dizionario, inizializza una coda per le sue note
                if robot_number not in self.local_music_map:
                    self.local_music_map[robot_number] = deque(maxlen=self.max_notes_per_neighbourg)

                # Aggiungi la nuova nota alla coda del robot
                self.local_music_map[robot_number].append(note)

            # Se il dizionario supera il numero massimo di robot, elimina il più vecchio
            while len(self.local_music_map) > self.max_music_neighbourgs:
                oldest_robot = next(iter(self.local_music_map))  # Prende la chiave più vecchia
                del self.local_music_map[oldest_robot]

            # Pulizia del buffer musicale dopo l'aggiornamento
            self.clean_music_buffer()
        else:
            print("No messages received. Skipping local music map update.")
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
        # Creare una rappresentazione pulita del dizionario
        clean_map = {
            robot_id: notes[0].midinote if notes else None  # Estrai il midinote dalla deque
            for robot_id, notes in self.local_music_map.items()
        }
        print(f"Robot {self.number} dictionary of others last played notes: {clean_map}")


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
                #self.set_note()
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
        self.set_note()
        for i in range(self.time_step):
            self.update_phase(millisecond,i)
        self.compute_robot_compass()
        
"""""

    def consult_local_music_dictionary(self):
        # return only the notes list in the dictionary
        all_notes = self.extract_notes_from_local_music_dictionary()
            
        # found scale with larager number of notes in common
        scale_matches = {}
        for scale_name, scale_notes in self.scales.items():
           # count how many notes of my neighbourhs are in the scale that I'm parsing.
            matching_notes = [note for note in all_notes if note in scale_notes]
            # counts yìthe number of notes in the scale I'm parsing.
            scale_matches[scale_name] = len(matching_notes)

        # Founds the scale with maximum notes in common.
        majority_scale = max(scale_matches, key=scale_matches.get)
        # to test the number of notes in common in that scale.
        number_of_notes_majority_scale = scale_matches[majority_scale]
        print("for r: "+ str(self.number)+ " the majority scale is: "+ str(majority_scale))
        # check if the note I play is already in the majority scale.
        
        if self.previous_midinote in self.scales[majority_scale]:
            print("r.: "+ str(self.number)+ " plays a note that is already in the majority scale, so repeats it.") 
            # is not my_prediciton but the belonging scale of the note.
            self.create_new_note(self.previous_midinote) 
        
        # i'm not playing a note from the majority scale.
        else:
            prob = random.random()
            if prob > 0.7:
               #print("robot n. "+ str(self.number) + " doesn't change note")
               self.create_new_note(self.previous_midinote)
               print( "r: "+ str(self.number)+ " isn't in majority but doesn't change note")
            else:
                # notes of the majority scale
                majority_scale_notes = self.scales[majority_scale]
                # founds the note in the majority scale that has the minimum distance with the played one.
                closest_note = min(majority_scale_notes, key=lambda x: abs(x - self.previous_midinote))
                # assign the closest note
                self.create_new_note(midi_value = closest_note) 

"""
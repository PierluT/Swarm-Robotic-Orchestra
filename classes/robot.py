
import math
import numpy as np
import time
import random
import datetime
from collections import defaultdict, deque
from classes.file_reader import File_Reader
from classes.dictionaries import colours,major_scales,major_pentatonic_scales, whole_tone_scales, orchestra_to_midi_range
from classes.tempo import Note

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Robot:
    
    def __init__(self, number, phase_period, delay_values, sb, time_signature, neighbors_number):
        self.number = number
        # value for robot set.
        self.radius = values_dictionary['radius']
        self.rectangleArea_width = values_dictionary['width_arena']
        self.rectangleArea_heigth = values_dictionary['height_arena']
        # value for collision
        self.radar_radius = values_dictionary['radar']
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
        # buffers for incoming and emmiting messages. 
        self.recieved_message = []
        self.forwarded_message = []
        # buffers for notes
        self.recieved_note = []
        self.forwarded_note = []
        self.last_played_ms = 0
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
        self.max_music_neighbourgs = 4
        self.max_notes_per_neighbourg = 1
        self.max_beats_per_neighbourg = 1
        # variable to control the previous midinote I played
        self.previous_midinote = 0
        # variable to control if in the previous iteraction I play in a common scale with neirghbourgs.
        self.scale_name = None
        self.probable_scales = []
        self.flag_included_proper_midinote = False
        self.harmony = False
        self.my_spartito = []
        # dictionary for recieved notes
        self.local_music_map = defaultdict(list)
        # dictionary for recieved timbre
        self.local_timbre_map = defaultdict(list)
        # dictionary for recieved delays
        self.local_beat_map = defaultdict(list)
        # dictionary for recieved phases
        self.local_phase_map = defaultdict(list) 
        self.timbre = ""
        self.timbre_dictionary = orchestra_to_midi_range
        self.delay = random.choice(delay_values) 
        # to found the minimum a maximum mid value.
        self.min_midinote = 0
        self.max_midinote = 0
        self.bar_phase_denominator = phase_period
        self.sb = sb
        # by now time signature is a value known from the robot
        self.time_signature = time_signature
        self.number_of_beats = time_signature[0]
        self.beat_phase = 0
        self.beat_phase_denominator = phase_period / self.number_of_beats
        #self.beat_counter = 1
        self.beat_counter = random.choice(delay_values)
        self.first_beat_control_flag = True
        self.threshold = 0
        self.last_beat_phase = 0
        self.neighbors_number = neighbors_number - 1

    def __repr__(self):
        return f"Robot(number = {self.number}, phase = {self.phase})"

    
    def compute_initial_x_position(self):
        possible_x_coordinate = random.randint(int(self.radar_radius + 10), int(self.rectangleArea_width - self.radar_radius - 10))
        return possible_x_coordinate
    
    def compute_initial_y_position(self):  
        possible_y_coordinate = random.randint(int(self.radar_radius + 10), int(self.rectangleArea_heigth - self.radar_radius - 10))
        return possible_y_coordinate
    
    def compute_beat_threshold(self):
        
        if self.sb == 0.5:
            self.threshold = 0.001
        if self.sb == 1:
            self.threshold = 0.01
        if self.sb == 2:
            self.threshold = 0.1


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

    
    # manage differently the collision
    def change_direction_x_axes(self):
        self.vx = -self.vx
                  
    def change_direction_y_axes(self):
        self.vy = -self.vy 
    
    #return angle direction in rad.
    def get_angle(self):
        return math.atan2(self.vx,self.vy)
    
    def move_robot(self, matrix_to_check, collision_threshold = 15):
        # method to compute the bussola for visualing robot orientation.
        self.compute_robot_compass()
        
        # Boundaries collision control
        if self.x - self.radar_radius <= 10 or self.x + self.radar_radius >= self.rectangleArea_width:
            self.change_direction_x_axes()
        if self.y - self.radar_radius <= 10 or self.y + self.radar_radius >= self.rectangleArea_heigth:
            self.change_direction_y_axes()
        
         # collision control with other robots
        for other_robot_index, distance in enumerate(matrix_to_check[self.number]):
            # Skip itself
            if other_robot_index == self.number:
                continue
            
            # Check if the distance is below the collision threshold
            if distance <= collision_threshold:
                self.change_direction_y_axes()
            
    def change_direction(self):
        # change direction with casual angle
        angle = random.uniform(0, 2 * math.pi)  
        speed = math.sqrt(self.vx**2 + self.vy**2) 
        self.vx = speed * math.cos(angle) 
        self.vy = speed * math.sin(angle)  
   
    def update_note(self):
        # extract only notes from my dictionary
        notes_to_check = [note[0] for note in self.local_music_map.values()]
        
        mas = 0
        scale_matches = {}
        for scale_name, scale_notes in self.scales.items():
            matching_notes = [note for note in notes_to_check if note in scale_notes]
            scale_matches[scale_name] = len(matching_notes)

            # found the scale with major number of common notes.
            max_matches = max(scale_matches.values())
            #mas = max_matches
        best_scales = [scale_name for scale_name, match_count in scale_matches.items() if match_count == max_matches]

        # control if my note is included in one of the probable scales:
        for scale in best_scales:
            #print("probable scale for r number: "+ str(self.number)+ " "+ str(scale))
            scale_notes = self.scales[scale]
            if self.note.pitch in scale_notes:
                 # put a flag if the note that I play is included in one of the best scales found for the harmony.
                self.flag_included_proper_midinote = True
                self.harmony = True
                #print("robot :"+ str(self.number)+ " is already in harmony")
        if not self.flag_included_proper_midinote:
            #print("note robot :"+ str(self.number)+" not included in the best scales")
            # function change 70-30 to call it or not.
            self.change_note(best_scales) 
            #print(self.note)

            
        self.flag_included_proper_midinote = False 
    
    # method to create the first note.
    def create_new_note(self, midi_value, bpm, duration):
        note = Note( midinote = midi_value, bpm = bpm, duration = duration)
        self.note = note
        #print("pitch: "+str(self.note.pitch))

    # mehtod to change the note if I'm not in harmony
    def change_note(self,best_scales):
        change_probability = random.random()
        # I change note
        if change_probability < 0.7:
            # I found the closest scale
            closest_scale = min(
                best_scales,
                key = lambda scale_name: min(
                    (self.note.pitch - note) if abs(self.note.pitch - note) <= 6 else 12 - abs(self.note.pitch - note)
                    for note in self.scales[scale_name]
                )
            )

            # found closest note into the closest scale.
            closest_note = min(
                self.scales[closest_scale],
                key = lambda note: min(abs(self.note.pitch - note), 12 - abs(self.note.pitch - note))
            )
            
            # Calcolo la differenza tra la nota suonata e la nota più vicina
            midi_diff = closest_note - self.note.pitch

            # Se la differenza è maggiore di 6, correggo il salto
            if abs(midi_diff) > 6:
                # Se la differenza è maggiore di 6, normalizzo il salto
                midi_diff = midi_diff - (12 if midi_diff > 0 else -12)
                print("here")

            # Aggiusto il midinote in base alla differenza
            self.note.midinote += midi_diff

            # Aggiorno il pitch alla nota più vicina
            self.note.pitch = closest_note

            # Stampa per il debug
            #print("pitch: " + str(self.note.pitch))
            #print("midinote: " + str(self.note.midinote))
            #print(self.note)
        if self.note.pitch > 11:
            print("NOOOOOOOOOOOOOOOOO")
            
    # message from each robot.
    def set_emitter_message(self):
        
        entry = {
            "robot number": self.number,
            "phase": self.phase,
            "note": self.note.pitch,
            "timbre": self.timbre,
            "beat": self.beat_counter,
        }
        self.forwarded_message = entry
        #print("nota "+str(self.note.pitch))
    
    # method to set the timbre based on related note ranges.
    def set_timbre_from_midi(self):

        matching_instruments = []
        for instruments in self.timbre_dictionary.values():
            for instrument, midi_range in instruments.items():
                # Verify if the note that I'm playing is in the midi range of the instrument
                if self.note.midinote in midi_range:  
                    matching_instruments.append(instrument)

        # If there are more than one corrispondent instrument, choose one randomly.
        if matching_instruments:
            choosen_timbre = random.choice(matching_instruments)
            #print(" found new instrument: " +str(choosen_timbre))
            self.timbre = choosen_timbre
        #else:
             #print("No matching instrument found") 

    # Every robot has a dictionary on what is the last note that others are playing.
    # With this structure I can predict the next note to play consulting music scales dictionary.
    # last 4 notes for every of my neighbourghs whom I reach treshold.
    def get_note_info(self):
        if self.recieved_message:
            for entry in self.recieved_message:  # Itera direttamente sui dizionari nel buffer
                if isinstance(entry, dict):  # Assicura che l'elemento sia un dizionario
                    robot_number = entry.get("robot number")
                    note = entry.get("note")
                    if robot_number is not None and note is not None:
                        # If the robot is not in the dictionar, initilize it.
                        if robot_number not in self.local_music_map:
                            self.local_music_map[robot_number] = deque(maxlen = self.max_notes_per_neighbourg)

                        # add a new note in the robot queue.
                        self.local_music_map[robot_number].append(note)
        
            
            # if the dictionary reaches maximum limit, remove the oldest data on it.
            while len(self.local_music_map) > self.max_music_neighbourgs:
                oldest_robot = next(iter(self.local_music_map))
                del self.local_music_map[oldest_robot]
            #print(self.local_music_map)
    
    # timbre dictionary with the same functions of notes dictionary
    def get_timbre_info(self):
        if self.recieved_message:
            for entry in self.recieved_message:
                if isinstance(entry, dict):
                    robot_number = entry.get("robot number")
                    timbre = entry.get("timbre")

                    if robot_number is not None and timbre is not None:
                        if robot_number not in self.local_timbre_map:
                            self.local_timbre_map[robot_number] = deque(maxlen=self.max_notes_per_neighbourg)
                        
                        self.local_timbre_map[robot_number].append(timbre)
            
            while len(self.local_timbre_map) > self.max_music_neighbourgs:
                oldest_timbre = next(iter(self.local_timbre_map))
                del self.local_timbre_map[oldest_timbre]
    
    # delay dictionary with the same functions of notes dictionary
    def get_beat_info(self):
        if self.recieved_message:
            for entry in self.recieved_message:
                if isinstance(entry, dict):
                    robot_number = entry.get("robot number")
                    beat = entry.get("beat")

                    if robot_number is not None and beat is not None:
                        # Inizializza la mappa per il robot se non esiste
                        if robot_number not in self.local_beat_map:
                            self.local_beat_map[robot_number] = beat  # Memorizza solo l'ultimo beat

                        # Aggiorna il beat del robot con il più recente
                        self.local_beat_map[robot_number] = beat

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

    # method to write robot music sheet.
    def add_note_to_spartito(self,ms):
        
        spartito_entry = {
            "ms": ms,
            "musician": self.number,
            "note": self.note.midinote,
            "dur": self.note.dur,
            "amp": self.note.amp,
            "bpm": self.note.bpm,
            "timbre": self.timbre,
            "delay": self.delay,
        }

        self.my_spartito.append(spartito_entry)
    
    # method to control that robot enters only the first time in the playing status.
    def control_playing_flag(self, millisecond):
        #if 0 <= self.phase < 1:
            # the first time that I enter means that I have to play.
            #if not self.triggered_playing_flag:
            self.playing_flag = True
            #self.triggered_playing_flag = True
            self.colour = colours['blue']
            self.last_played_ms = millisecond
                # that has to be separated by the 0 cross phase.
            self.add_note_to_spartito(millisecond)  
        # Means that my phase doesn't allow me to play.
        #else:
            # to control that the robot doesn't start to play the note before the end of previous one.
            # first term: elapsed amount of time from last played ms and current millisecond.
            # second term: beats multiplied per ms in a second divided all by beats in a second.
            if( (millisecond - self.last_played_ms) >  (1000 * self.sb)):
                # add a condition that the else condition happens only after the end of the note.
                self.triggered_playing_flag = False
                self.playing_flag = False
                self.colour = colours['green']
    
    # method to update internal robot phase.
    def update_phase(self,millisecond):
        self.phase += (2 * np.pi / self.bar_phase_denominator)
        # normalization only if I reach 2pi then I go to 0.
        self.phase %= (2 * np.pi)
        # method to control if I have the permission to play.
        self.control_playing_flag(millisecond)
    
    def get_phase_info(self):
        if self.recieved_message:
            for entry in self.recieved_message:  
                if isinstance(entry, dict):  
                    robot_number = entry.get("robot number")
                    phase_value = entry.get("phase")
                    if robot_number is not None and phase_value is not None:
                        self.local_phase_map[robot_number].append(phase_value)

    # Method for Kuramoto model
    def update_phase_kuramoto_model(self):
        # Iterate on all the recieved phases and apply Kuramoto model.
        for robot_number, phases in self.local_phase_map.items():
            for recieved_phase in phases:
                self.phase += self.K * np.sin(recieved_phase - self.phase)
                # phase normalization.
                self.phase %= (2 * np.pi)
        
        # clear the dictionary after computing values.
        self.local_phase_map.clear()
  
    def update_beat_phase(self, millisecond):
        self.beat_phase += (2 * np.pi / self.beat_phase_denominator) 
        # normalization only if I reach 2pi then I go to 0.
        self.beat_phase %= (2 * np.pi)
        self.control_beat_flag(millisecond)
    
    def control_beat_flag(self, millisecond):

        if 0 <= self.beat_phase < self.threshold:
            # I control that I not already increment in the fisrt control.
            if not self.first_beat_control_flag: 
                # if beat counter reaches the number of beats is reset to zero.
                self.beat_counter += 1 if self.beat_counter < self.number_of_beats else -self.beat_counter + 1
                # set the flag true of the first control.
                self.first_beat_control_flag = True 
        else:
            self.first_beat_control_flag = False 
        
        if self.beat_counter == 1:
            self.last_played_ms = millisecond
            self.playing_flag = True
            # to control that I play for the correct amount of time
            if( (millisecond - self.last_played_ms) >  (1000 * self.sb)):
                self.playing_flag = False
        
        else:
            self.playing_flag = False




"""""

    # method to control that robot enters only the first time in the playing status.
    def control_playing_flag(self, millisecond):
        if 0 <= self.phase < 1:
            # the first time that I enter means that I have to play.
            if not self.triggered_playing_flag:
                self.playing_flag = True
                self.triggered_playing_flag = True
                self.colour = colours['blue']
                self.last_played_ms = millisecond
                # that has to be separated by the 0 cross phase.
                self.add_note_to_spartito(millisecond)  
            # Means that is not the first time that I enter in the condition, so I have to reset false.
            else:
                self.playing_flag = False
                self.colour = colours['blue']
        # Means that my phase doesn't allow me to play.
        else:
            # to control that the robot doesn't start to play the note before the end of previous one.
            # first term: elapsed amount of time from last played ms and current millisecond.
            # second term: beats multiplied per ms in a second divided all by beats in a second.
            if( (millisecond - self.last_played_ms) >  (1000 * self.sb)):
                # add a condition that the else condition happens only after the end of the note.
                self.triggered_playing_flag = False
                self.playing_flag = False
                self.colour = colours['green']

"""
                    
    






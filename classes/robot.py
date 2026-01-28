import math
import numpy as np
import random
import math
import os
from collections import defaultdict, deque
from configparser import ConfigParser
import matplotlib.pyplot as plt
from classes.dictionaries import colours, major_scales, major_pentatonic_scales, whole_tone_scales, orchestra_to_midi_range, instrument_ensembles
from classes.tempo import Note


# Leggi il file
config = ConfigParser()
config.read('configuration.ini')

class Robot:
    
    def __init__(self, number, phase_period, delay_values, sb, time_signature,
                 delta_val, total_robots, status, scales_to_use):
        self.number = number
        self.status = status
        self.time = int(config['PARAMETERS']['milliseconds'])
        # time to repair 
        self.off_duration = 60000 if status == "off" else 0
        # time to die 
        self.on_duration = 60000 if status == "on" else 0
        # to keep track of the moment when the robot switches off.
        self.off_start_time = 0 if status == "off" else None
        # to keep track of the moment when the robot switches on.
        self.on_start_time = 0 if status == "on" else None
        self.total_robots = total_robots
        # value for robot set.
        self.radius = int(config['PARAMETERS']['radius'])
        self.rectangleArea_width = int(config['PARAMETERS']['width_arena'])
        self.rectangleArea_heigth = int(config['PARAMETERS']['height_arena'])
        self.colour = colours['green']
        self.velocity = float(config['PARAMETERS']['velocity'])
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
        # MUSIC VARIABLES
        self.scales = scales_to_use
        self.note = None
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
        self.d_values =[value for value in delay_values]
        self.delay = random.choice(delay_values) 
        # to found the minimum a maximum mid value.
        self.min_midinote = 0
        self.max_midinote = 0
        self.bar_phase_denominator = phase_period
        self.sb = sb
        self.bar = 0
        # by now time signature is a value known from the robot
        self.time_signature = time_signature
        self.number_of_beats = time_signature[0]
        #self.beat_phase = 0
        self.beat_phase = np.random.uniform(0, 2 * np.pi)
        self.beat_phase_denominator = phase_period / self.number_of_beats
        #self.beat_counter = random.choice(self.d_values)
        self.beat_counter = max(self.d_values, key=lambda val: abs(val - self.delay))
        self.first_beat_control_flag = True
        self.threshold = 0
        self.last_beat_phase = 0
        # ORCHESTRA SPARTITO
        self.orchestra_spartito = []
        self.ms_dynamic_ff = []
        self.music_map = deque(maxlen = 4)
        self.first_beat_ms = 0
        self.first_saved_beat = False
        self.supposed_scales = []
        # TIMBRE MODULE
        # boolean for the first call of the method
        self.first_call = True
        # learning rate for thresholds
        self.learing_rate = 8
        # forgetting rate for thresholds
        self.forgetting_rate = 3
        # variables for stimuli
        self.stimuli_update_mode = config['PARAMETERS']['stimuli_update']
        self.alpha = 3
        self.delta = delta_val
        self.min_delta = 0.5
        #self.delta_incidence = values_dictionary['delta_incidence']
        # variabile to store robots that played on this measure
        self.robots_that_played = set()
        self.prev_musicians_count = 0
        # variable to listen if someone new joined the jam session.
        self.musicians_seen = set()
        # variable to check if everybody has palyed and so I can update stimuli.
        self.reset_count = 0
        # corresponds to number of the tasks.
        self.timbre_dictionary = orchestra_to_midi_range
        self.num_timbres = sum(len(instruments) for instruments in self.timbre_dictionary.values())
        self.timbre_list = [instrument for instruments in self.timbre_dictionary.values() for instrument in instruments]
        self.stimuli = {timbre: 500 for timbre in self.timbre_list}
        # to print stimuli history.
        self.timbre_stimuli_history = []
        self.timbre_stimuli_history.append(self.stimuli.copy())
        self.target_distribution = np.array([])
        self.timbre = ""
        self.timbre_thresholds = {timbre: 500 for timbre in self.timbre_list}
        self.timbre_threshold_history = []
        self.timbre_threshold_history.append(self.timbre_thresholds.copy())
        self.last_timbre = None  # Ultimo timbro suonato
        self.distribution_matches = True
        #self.reached_target_distribution = False
        # AVAILABLE ENSEMBLES
        self.ensembles = instrument_ensembles
        self.a = 0
        self.b = 0

    def __repr__(self):
        return f"Robot(number = {self.number}, phase = {self.phase})"

    def compute_initial_x_position(self):
        possible_x_coordinate = random.randint(int(self.radius + 10), int(self.rectangleArea_width - self.radius - 10))
        return possible_x_coordinate
    
    def compute_initial_y_position(self):  
        possible_y_coordinate = random.randint(int(self.radius + 10), int(self.rectangleArea_heigth - self.radius - 10))
        return possible_y_coordinate
    
    def compute_beat_threshold(self):
        # Aumento la threshold per BPM più alti
        if self.sb == 0.5:
            self.threshold = 0.5  # Valore più grande per permettere il reset
        
        elif self.sb == 1:
            self.threshold = 0.2
        
        elif self.sb == 2:
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
        # buffers for local communication
        self.forwarded_message.clear()
        self.recieved_message.clear()
        # buffer for instantneous note
        self.my_spartito.clear()
        # buffer for neighbors notes
        self.orchestra_spartito.clear()
        # buffer for notes played by neighbors
        # PROVARE CON music_map non pulito qui
        #self.music_map.clear()
        # buffer for robot harmony suppositions.
        self.supposed_scales.clear()

    # manage differently the collision
    def change_direction_x_axes(self):
        self.vx = -self.vx  # Inverti direzione
        self.x += self.vx
                  
    def change_direction_y_axes(self):
        self.vy = -self.vy  # Inverti direzione
        self.y += self.vy 
    
    #return angle direction in rad.
    def get_angle(self):
        return math.atan2(self.vx,self.vy)
    
    def move_robot(self,new_x, new_y, new_vx, new_vy):
        self.x = new_x
        self.y = new_y
        self.vx = new_vx
        self.vy = new_vy
        # method to compute the bussola for visualing robot orientation.
        self.compute_robot_compass()
        # Boundaries collision control
        if self.x - self.radius <= 10 or self.x + self.radius >= self.rectangleArea_width:
            self.change_direction_x_axes()
        if self.y - self.radius <= 10 or self.y + self.radius >= self.rectangleArea_heigth:
            self.change_direction_y_axes()

    # method to set the dynamics based on the delay, to stress the first note of the measure.
    def set_dynamic(self):
        if self.delay == 1:
            self.note.dynamic = "ff"
        else:
            self.note.dynamic = "mf"
    
    # method to to compute harmonicity with other robots.
    def update_note(self):
        # I store note info.
        for entry in self.orchestra_spartito: 
            note = entry.get("note") 
            if note is not None:
                pitch_note = note % 12
                self.music_map.append(pitch_note)  # If it's full, it removes the older one.
        
        # --- NEW: wait until music_map is full ---
        if len(self.music_map) < self.music_map.maxlen:
            # Not enough information to infer a scale yet
            return
        
        # extract only notes from my dictionary
        notes_to_check = list(self.music_map)
        #mas = 0
        scale_matches = {}
        # method to found the scale with best matches with my notes list. 
        for scale_name, scale_notes in self.scales.items():
            matching_notes = [note for note in notes_to_check if note in scale_notes]
            scale_matches[scale_name] = len(matching_notes)

        # found the scale with major number of common notes.
        max_matches = max(scale_matches.values())
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
        self.supposed_scales = best_scales
        #print(self.number, " supposed scales: ", self.supposed_scales)
        
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
            #print("robot ", self.number, " changes note")
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
            #print("robot ", self.number," closest scale ", closest_scale, " closest note ", closest_note)
            #print("robot ", self.number," changes from ", self.note.pitch, " to ", closest_note)
            
            # Calcolo la differenza tra la nota suonata e la nota più vicina
            midi_diff = closest_note - self.note.pitch

            # Se la differenza è maggiore di 6, correggo il salto
            if abs(midi_diff) > 6:
                # Se la differenza è maggiore di 6, normalizzo il salto
                midi_diff = midi_diff - (12 if midi_diff > 0 else -12)
                #print("here")

            # Aggiorno il pitch alla nota più vicina
            self.note.pitch = closest_note
            # Aggiusto il midinote in base alla differenza
            #midinote_to_test = self.note.midinote + midi_diff
            
            # Aggiusto il midinote in base alla differenza
            #self.note.midinote += midi_diff
            plausible_new_midinote = self.note.midinote + midi_diff
            
            midi_range_for_control = self.get_midi_range_from_timbre()

            if plausible_new_midinote in midi_range_for_control:
                self.note.midinote += midi_diff
            else:
                #print(f"Pitch relativo da cercare: {self.note.pitch}")
                new_midinote = self.find_closest_midinote(midi_range_for_control)
                self.note.midinote = new_midinote
                #print(f"Nuova nota MIDI: {new_midinote}")
            #print("pitch: " + str(self.note.pitch))
            #print("midinote: " + str(self.note.midinote))
            #print(self.note)
        if self.note.pitch > 11:
            print("NOOOOOOOOOOOOOOOOO")
        print()  

    # return the range of the actual timbre.
    def get_midi_range_from_timbre(self):
        midi_range = None
        for category in self.timbre_dictionary.values():
            if self.timbre in category:
                midi_range = category[self.timbre]
                break  # exit the loop once the timbre is found
        
        return midi_range

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
    
    # method to set the timbre based on thresholds and stimuli.
    def choose_timbre(self):
        #self.a += 1
        chosen_timbre = None
        probabilities = {}
        # compute the probabilities to choose each timbre
        for timbre in self.timbre_list:
            stim = self.stimuli[timbre]
            threshold = self.timbre_thresholds[timbre]
            prob = stim ** 2 / (stim ** 2 + threshold ** 2)
            probabilities[timbre] = prob
        # Sort the probabilities by increasing value
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1])
        # Extract only the value
        prob_values = [p for _, p in sorted_probs]
        # norm probabilities to sum to 1
        total = sum(prob_values)
        normalized_probs = [p / total for p in prob_values]
        # compute intervals
        cumulative_probs = []
        cumulative_sum = 0
        for p in normalized_probs:
            cumulative_sum += p
            cumulative_probs.append(cumulative_sum)
        r = random.random()
        # find on wich interval the random number falls
        for i, cum_prob in enumerate(cumulative_probs):
            if r <= cum_prob:
                chosen_timbre = sorted_probs[i][0]  
                break    
        # if thres's the first call and I don't have a timbre, I choose the one with the highest probability.
        if self.first_call and chosen_timbre is None:
                chosen_timbre = self.timbre_list[np.argmax(probabilities)]
        # if I didn't choose anything for probabilites I stick with the last timbre.           
        if chosen_timbre is None:
            chosen_timbre = self.last_timbre
        # Update the timbre with the new one.
        self.timbre = chosen_timbre
        self.last_timbre = chosen_timbre
        # Threshold's updates based on choosen timbre.
        self.update_thresholds(chosen_timbre)
        new_midi_range = self.get_midi_range_from_timbre()
        # only from the second method call: I check if the midinote is within the range of my new timbre,
        # otherwise I change note octave. 
        if not self.first_call:
            if self.note.midinote in new_midi_range:
                return
            else:
                #print(self.note.midinote, " non è nel range del nuovo timbro", self.timbre)
                #print(f"Pitch relativo da cercare: {self.note.pitch}")
                new_midinote = self.find_closest_midinote(new_midi_range)
                self.note.midinote = new_midinote
                #print(f"Nuova nota MIDI: {new_midinote}")
        # once I enter into the method for the first time I set the first call to false.
        self.first_call = False  
        return chosen_timbre
    
    def update_thresholds(self, chosen_timbre):
        if chosen_timbre is None:
            print("problemaaaaaaaaaaaaaaaaaaaaa")
            return 
        # Aggiornamento delle soglie
        for timbre in self.timbre_list:
            if timbre == chosen_timbre:
                # Rinforzo positivo: abbassa la soglia per il timbro scelto
                self.timbre_thresholds[timbre] = max(10, self.timbre_thresholds[timbre] - self.learing_rate)
            else:
                # Rinforzo negativo: aumenta le soglie degli altri timbri
                self.timbre_thresholds[timbre] = min(1000, self.timbre_thresholds[timbre] + self.forgetting_rate)
        # Salvataggio dello stato attuale nella storia delle soglie
        self.timbre_threshold_history.append(self.timbre_thresholds.copy())

    def find_closest_midinote(self, new_midi_range):
        """
        Trova la nota MIDI più vicina con lo stesso pitch (altezza relativa) nel nuovo range.
        
        :param new_midi_range: Lista di note MIDI disponibili per il nuovo timbro.
        :return: La nota MIDI più vicina con lo stesso pitch, oppure None se nessuna nota è trovata.
        """
        matching_notes = [note for note in new_midi_range if note % 12 == self.note.pitch]
        #print(f"Note corrispondenti: {matching_notes}")

        if matching_notes:
            # Scegli la nota più vicina all'originale
            closest_midinote = min(matching_notes, key=lambda x: abs(x - self.note.midinote))
            #print(f"Nota più vicina trovata: {closest_midinote}")
            return closest_midinote  # Restituisce la nuova nota MIDI
        else:
            #print("Nessuna nota con lo stesso pitch trovata nel nuovo range.")
            return None  # Nessuna nota corrispondente trovata

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
            "dynamic": self.note.dynamic,
            "bpm": self.note.bpm,
            "timbre": self.timbre,
            "delay": self.delay,
            "beat phase": self.beat_phase,
            "harmony": self.harmony
        }

        self.my_spartito.append(spartito_entry)
        # when I play a note I add to the list of heard notes the note I played and wich instrument I played.
        self.robots_that_played.add((self.number, self.timbre))
    
    # kuramoto model that works with orchestra spartito 
    def update_phase_kuramoto_model(self):
        for entry in self.orchestra_spartito:
            #if entry["ms"] == millisecond:
            received_phase = entry["beat phase"]
            self.beat_phase += self.K * np.sin(received_phase - self.beat_phase)
        # normalization
        self.beat_phase %= (2 * np.pi)
    
    # method to increment the phase value
    def update_beat_phase(self, millisecond):
        self.beat_phase += (2 * np.pi / self.beat_phase_denominator) 
        # normalization only if I reach 2pi then I go to 0.
        self.beat_phase %= (2 * np.pi)
        # method to check the beat number, the bar number and If I have to play. 
        self.control_beat_flag(millisecond)
    
    # method to control the beat, bars and the reletive colour.
    def control_beat_flag(self, millisecond):
        # If I crossed the zero phase ( threshold is different depending on the BPM and the numerator in time signature).    
        if 0 <= self.beat_phase < self.threshold:  
            # condition to avoid the first beat control flag to be set to true in the first iteration.
            if not self.first_beat_control_flag:  
                if self.beat_counter < self.number_of_beats:
                    self.beat_counter += 1
                else:
                    self.beat_counter = 1
                    self.bar += 1
                    self.robots_that_played.clear()
                    if self.distribution_matches == False:
                        self.choose_timbre()

                self.first_beat_control_flag = True

        else:
            self.first_beat_control_flag = False  
        # LOGIC TO UPDATE MY SPARTITO.
        # if the beat where I am corresponds to the beat where I have to play, I set the colour to grey and I play.
        if self.beat_counter == self.delay:
            self.colour = colours['red']
            # boolean to declare "play" state only once.
            if not self.triggered_playing_flag:
                self.playing_flag = True
                self.triggered_playing_flag = True
                self.last_played_ms = millisecond
                self.add_note_to_spartito(millisecond)
            else:
                self.playing_flag = False  
        else:
            self.playing_flag = False
            self.triggered_playing_flag = False
            
        # to save first beat millisecond
        if self.beat_counter == 1:
            self.colour = colours['black']
            if not self.first_saved_beat:
                self.first_beat_ms = millisecond
                self.first_saved_beat = True
        else:
            self.first_saved_beat = False        
        
        # if no one of the previous conditions is true, than the color depends on the timbre.
        if self.beat_counter != self.delay and self.beat_counter != 1:
            
            if self.timbre == "Fl":
                self.colour = colours['pink']
            elif self.timbre == "ClBb":
                self.colour = colours['purple']
            elif self.timbre == "Bn":
                self.colour = colours['blue']
            elif self.timbre == "TpC":
                self.colour = colours['yellow']
            elif self.timbre == "Tbn":
                self.colour = colours['orange']
            elif self.timbre == "BTb":
                self.colour = colours['brown']
            # Archi
            elif self.timbre == "Vn":
                self.colour = colours['light_blue']
            elif self.timbre == "Va":
                self.colour = colours['pink']
            elif self.timbre == "Vc":
                self.colour = colours['dark_blue']
            elif self.timbre == "Cb":
                self.colour = colours['sky_blue']
            # Legni
            elif self.timbre == "Ob":
                self.colour = colours['green']
            elif self.timbre == "ASax":
                self.colour = colours['orange']
            # Ottoni
            elif self.timbre == "Hn":
                self.colour = colours['olive']
            elif self.timbre == "Acc":
                self.colour = colours['turquoise']
        
    # robot's ears simulation.
    def update_orchestra_spartito(self, full_spartito, millisecond):
        
        if not full_spartito:
            return 
        new_musician_joined = False
        # I store only entries that are not from myself and that are at the current millisecond.
        current_entries = [
            entry for entry in full_spartito 
            if entry["musician"] != self.number and entry["ms"] == millisecond
        ]
        
        # update the orchestra spartito with the current entries.
        self.orchestra_spartito.extend(current_entries)
        
        # add musicians that played in this measure.
        self.robots_that_played.update(
            (entry["musician"], entry["timbre"]) for entry in current_entries
        )
        
        # Check if there're any new musicians.
        for entry in current_entries:
            musician_id = entry["musician"]
            if musician_id not in self.musicians_seen:
                self.musicians_seen.add(musician_id)
                new_musician_joined = True
        
        # if I listen some new musician I update the target and instrument distribution.
        if new_musician_joined:
            self.update_target_and_instrument_distribution()
        
        if self.orchestra_spartito:
            # HARMONY MODULE
            self.update_note()
            # KURAMOTO MODULE
            self.update_phase_kuramoto_model()
            # FIREFLY MODULE
            self.update_beat_firefly()
            # BIO-INSPIRED MODULE.
            self.update_stimuli()

        if self.distribution_matches:
            self.b+=1
        unique_musicians = {robot for robot, _ in self.robots_that_played}
        current_count = len(unique_musicians)
    
    """            
        # I check if every robot has played.  
        unique_musicians = {robot for robot, _ in self.robots_that_played}    
        if len(unique_musicians) == self.total_robots and self.distribution_matches == False:
            # TIBRE MODULE
            self.choose_timbre()
            self.robots_that_played.clear()   
    """         
    
    # method to update beat with firefly algorithm.
    def update_beat_firefly(self):
        # Trova tutti gli eventi con dynamic == 'ff'
        ff_entries = []
        for entry in self.orchestra_spartito:
            if entry["dynamic"] == "ff":
                ff_entries.append(entry)
                
        if not ff_entries:
            return  # Nessuna nota con 'ff', non serve sincronizzare
        
        first_ff = ff_entries[0]  # Usa il primo elemento della lista
        ms_ff_iniziale = first_ff["ms"]
        
        # NOT THE LAST TIME YOU PLAYED, BUT THE LAST TIME YOU THINK YOU CROSSED BEAT 1.
        # ABOUT MY PERCEPTION OF WHERE IS THE START OF THE MEASURE.
        relative_time = ms_ff_iniziale - self.first_beat_ms
        
        #print("robot ", self.number, " ms ff iniziale ",ms_ff_iniziale )
        #print("robot ", self.number, " last first beat ms: ", self.last_played_ms) 

        # I compute the tieme interval from my last played note and the fortissimo note suddenly listened.
        
        #print("robot ", self.number, "relative time ", relative_time, " at ms ", millisecond)
        #print("self sb ", self.sb)

        # to compute in wich beat I am, computing from the milliseconds infos, beacuse I'm supposed to not know this info 
        # from a real point of view.
        actual_beat = (relative_time / (self.beat_phase_denominator) ) +1
        #print("robot ", self.number, "actual beat ", actual_beat, " at ms ", millisecond)
        
        # If the actual beat is not an integer, it means that we are in the first stesp of the simualtions,
        # so the phase is not synchronized and it doesn't make sense syncronyze beat before phase.
        if actual_beat % 1 != 0:
            #print("robot ", self.number, " non sincronizzato, esco dal metodo.")
            #print()
            return
        
        if actual_beat == self.number_of_beats:
            self.beat_counter = 1
            return
        diff = actual_beat - 1  # Il primo ff è sempre beat 1
        
        #print("difference", diff)
        if diff == 0:
            #print(print(f"robot {self.number} non si sposta"))
            return
        # I divide the measure in 2 parts to understand if is better go to the left or to the right.
        half_beats = self.number_of_beats / 2

        if diff <= half_beats:
            move = -1
        else:
            move = 1
        self.beat_counter += move
        #print(f"robot {self.number} si sposta di {move} beat")
    
    def print_threshold_history(self, base_folder_path):
        thresholds_dir = os.path.join(base_folder_path, "thresholds")
        os.makedirs(thresholds_dir, exist_ok=True)

        threshold_history = np.array([
            [step[t] for t in self.timbre_list]
            for step in self.timbre_threshold_history
        ])

        fig, ax = plt.subplots(figsize=(20, 15))

        for i, timbre in enumerate(self.timbre_list):
            ax.plot(threshold_history[:, i])

        ax.set_xlabel("Time", fontsize=40)
        ax.set_ylabel("Threshold", fontsize=40)
        ax.set_title(f"Threshold Evolution for Robot {self.number + 1}", fontsize=40)

        ax.tick_params(axis='both', labelsize=16)

        plt.tight_layout()

        filename = f"robot_{self.number + 1}_thresholds.png"
        save_path = os.path.join(thresholds_dir, filename)

        plt.savefig(save_path, bbox_inches="tight")
        plt.close()


    def print_stimuli_history(self, base_folder_path):

        stimuli_dir = os.path.join(base_folder_path, "stimuli")
        os.makedirs(stimuli_dir, exist_ok=True)

        stimuli_array = np.array([
            [step[t] for t in self.timbre_list]
            for step in self.timbre_stimuli_history
        ])

        fig, ax = plt.subplots(figsize=(20, 15))

        for i, timbre in enumerate(self.timbre_list):
            ax.plot(stimuli_array[:, i])

        ax.set_xlabel("Time (s)", fontsize=40)
        ax.set_ylabel("Stimulus Value", fontsize=40)
        ax.set_title(f"Stimuli Evolution for Robot {self.number + 1}", fontsize=40)

        ax.tick_params(axis='both', labelsize=16)

        plt.tight_layout()

        filename = f"robot_{self.number + 1}_stimuli.png"
        save_path = os.path.join(stimuli_dir, filename)

        plt.savefig(save_path, bbox_inches="tight")
        plt.close()


    def compute_task_performed(self):
        timbre_counts = {}
        # counts how many times each timbre has been played by the robots.
        for robot, timbre in self.robots_that_played:
            if timbre in timbre_counts:
                # if the timbre is already in the dictionary, increment the count
                timbre_counts[timbre] = timbre_counts[timbre] + 1
            else:
                
                timbre_counts[timbre] = 1

        task_performed = {}
        # if some timbres have not been played, I set the value to 0.
        for timbre in self.timbre_list:
            if timbre in timbre_counts:
                task_performed[timbre] = timbre_counts[timbre]
            else:
                task_performed[timbre] = 0

        return task_performed
    
    def update_stimuli(self):
        # I compute the timbres perfromed by the robots to compute what is needed to be played.
        task_performed = self.compute_task_performed()
        total_tasks = sum(task_performed.values())
        # to see current distributions
        current_distribution = {}
        for timbre in self.timbre_list:
            current_distribution[timbre] = task_performed.get(timbre, 0) / total_tasks
        # check if the current distribution matches the target distribution
        self.distribution_matches = True
        for timbre, target_value in self.target_distribution.items():
            actual_value = current_distribution.get(timbre, 0)
            if actual_value != target_value:
                self.distribution_matches = False
                # exit from the cycle.
                break
        
        if self.distribution_matches:
            #print("combacia")
            # if it matches I exit the method.
            return

        if self.stimuli_update_mode == "delta":
            max_delta = self.delta
            # MODIFIED STIMULI UPDATE FORMULA
            # try to remove alpha from the formula.
            # WORKS
            #self.stimuli += self.delta * delta_distribution - (self.alpha / self.total_robots) * task_performed
            #self.stimuli += self.delta * delta_distribution
            
            for timbre, target_value in self.target_distribution.items():
                actual_value = current_distribution.get(timbre, 0)
                difference = target_value - actual_value
                abs_diff = abs(difference)
                
                scaled_delta = np.clip(abs_diff * max_delta, self.min_delta, max_delta)
                #self.stimuli[timbre] += self.delta * difference
                self.stimuli[timbre] += np.sign(difference) * scaled_delta
        else:
            # STANDARD UPDATE FORMULA
            self.stimuli += self.delta - (self.alpha / self.total_robots) * task_performed
        
        # Clipping of the values to ensure they stay within the range [1, 1000]
        for timbre in self.stimuli:
            self.stimuli[timbre] = min(max(self.stimuli[timbre], 1), 1000)
        self.timbre_stimuli_history.append(self.stimuli.copy())
        self.reset_count += 1  
    
    # method to update the target distribution based on the musicians seen.
    def update_target_and_instrument_distribution(self):
        number_of_instruments = round((len(self.musicians_seen) + 1) / max(self.d_values))
        if number_of_instruments > 0:
            # Recupera l'ensemble desiderato in base al numero
            instruments = self.ensembles.get(number_of_instruments, [])
            total = len(instruments)
            # Costruisce una distribuzione per tutti i timbri (anche quelli non selezionati)
            self.target_distribution = {}
            for timbre in self.timbre_list:
                if timbre in instruments:
                    self.target_distribution[timbre] = 1 / total
                else:
                    self.target_distribution[timbre] = 0.0
        else:
            # Nessuno strumento target → tutti a 0
            self.target_distribution = {timbre: 0.0 for timbre in self.timbre_list}

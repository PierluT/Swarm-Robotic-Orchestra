
import math
import numpy as np
import time
import random
import math
import datetime
import os
from collections import defaultdict, deque
import matplotlib.pyplot as plt
from classes.file_reader import File_Reader
from classes.dictionaries import colours, major_scales, major_pentatonic_scales, whole_tone_scales, orchestra_to_midi_range
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
        self.scales = major_pentatonic_scales
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
        self.d_values =[value for value in delay_values if value != 1]
        self.delay = random.choice(delay_values) 
        # to found the minimum a maximum mid value.
        self.min_midinote = 0
        self.max_midinote = 0
        self.bar_phase_denominator = phase_period
        self.sb = sb
        # by now time signature is a value known from the robot
        self.time_signature = time_signature
        self.number_of_beats = time_signature[0]
        #self.beat_phase = 0
        self.beat_phase = np.random.uniform(0, 2 * np.pi)
        self.beat_phase_denominator = phase_period / self.number_of_beats
        #self.beat_counter = 1
        #self.beat_counter = random.choice(self.d_values)
        self.beat_counter = random.choice([val for val in self.d_values if val != self.delay])
        self.first_beat_control_flag = True
        self.threshold = 0
        self.last_beat_phase = 0
        self.neighbors_number = neighbors_number - 1
        # orchestra spartito
        self.orchestra_spartito = []
        self.ms_dynamic_ff = []
        self.music_map = deque(maxlen = self.neighbors_number)
        self.first_beat_ms = 0
        self.first_saved_beat = False
        self.supposed_scales = []
        # BIO-INSPIRED VARIABLES
        # Booleano per tracciare la prima chiamata
        self.first_call = True
        # learning rate
        self.learing_rate = 10
        # forgetting rate
        self.forgetting_rate = 3
        # probability to stop the task
        self.p = 0.2
        self.timbre_dictionary = orchestra_to_midi_range
        self.timbre_list = [instrument for instruments in self.timbre_dictionary.values() for instrument in instruments]
        self.timbre = ""
        self.num_timbres = sum(len(instruments) for instruments in self.timbre_dictionary.values())
        self.timbre_thresholds =  np.full(self.num_timbres, 500, dtype=float)
        self.timbre_threshold_history = []
        self.timbre_threshold_history.append(self.timbre_thresholds.copy())
        self.last_timbre = None  # Ultimo timbro suonato
        self.elle = 0
        self.effe = 0


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
        self.music_map.clear()
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
        for sublist in self.orchestra_spartito:  
            for entry in sublist: 
                note = entry.get("note")  
                if note is not None:
                    pitch_note = note % 12
                    self.music_map.append(pitch_note)  # If it's full, it removes the older one.

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

            # Stampa per il debug
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
                break  # Esci appena trovi il range corretto
        
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
    def choose_timbre(self, stimuli):
        self.elle += 1
        chosen_timbre = None
        probabilities = []
        
        # compute the probabilities to choose each timbre
        for j in range(self.num_timbres):
            prob = stimuli[j] ** 2 / (stimuli[j] ** 2 + self.timbre_thresholds[j] ** 2)
            probabilities.append(prob)
        
        # Choose the timbre based on the probabilities
        for j, prob in enumerate(probabilities):
            if random.random() < prob:
                chosen_timbre = self.timbre_list[j]
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
        # # otherwise I change note octave. 
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
    
    # method to update thresholds based on chosen timbre.
    def update_thresholds(self, chosen_timbre):
        # no change
        if chosen_timbre is None:
            print("problemaaaaaaaaaaaaaaaaaaaaa")
        # Trova l'indice del timbro scelto
        #print(f"R: ", self.number, " Updating thresholds for chosen timbre: {chosen_timbre}")
        chosen_index = self.timbre_list.index(chosen_timbre)
        task_performed = np.zeros(self.num_timbres)  # Indica se il timbro è stato scelto (1 se sì, 0 se no)
        
        # Aggiornamento delle soglie
        for j in range(self.num_timbres):
            if j == chosen_index:
                # Rinforzo positivo: abbassa la soglia per il timbro scelto
                self.timbre_thresholds[j] = max(10, self.timbre_thresholds[j] - self.learing_rate)
            else:
                # Rinforzo negativo: aumenta le soglie degli altri timbri
                self.timbre_thresholds[j] = min(1000, self.timbre_thresholds[j] + self.forgetting_rate)
        
        # Salvataggio dello stato attuale nella storia delle soglie
        self.timbre_threshold_history.append(self.timbre_thresholds.copy())
        #print(f"Threshold history updated: {self.timbre_threshold_history}")

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
    
    # method to update internal robot phase.
    def update_phase(self,millisecond):
        self.phase += (2 * np.pi / self.bar_phase_denominator)
        # normalization only if I reach 2pi then I go to 0.
        self.phase %= (2 * np.pi)
        # method to control if I have the permission to play.
        self.control_playing_flag(millisecond)
    
    # kuramoto model that works with orchestra spartito 
    def update_phase_kuramoto_model(self, millisecond):
        
        for sublist in self.orchestra_spartito:
            for entry in sublist:
                if entry["ms"] == millisecond:  # Filtra solo l'entry corrispondente al millisecondo attuale
                    received_phase = entry["beat phase"]
                    self.beat_phase += self.K * np.sin(received_phase - self.beat_phase)

        # Normalizzazione della fase nel range [0, 2π]
        self.beat_phase %= (2 * np.pi)

    def update_beat_phase(self, millisecond):
        self.beat_phase += (2 * np.pi / self.beat_phase_denominator) 
        # normalization only if I reach 2pi then I go to 0.
        self.beat_phase %= (2 * np.pi)
        self.control_beat_flag(millisecond)
    
    # method to control the beat and the reletive colour.
    def control_beat_flag(self, millisecond):
        # LOGICA PER GESTIRE IL BEAT
        if 0 <= self.beat_phase < self.threshold:  
            
            if not self.first_beat_control_flag:  
                self.beat_counter = self.beat_counter + 1 if self.beat_counter < self.number_of_beats else 1
                self.first_beat_control_flag = True  
        else:
            self.first_beat_control_flag = False  
        
        # LOGIC TO UPDATE MY SPARTITO.
        # ADD DELAY VALUE TO SIMULATE IN A MORE REALISTIC WAY.
        if self.beat_counter == self.delay:
            self.colour = colours['grey']
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
        
        # Se nessuna delle due condizioni precedenti, il colore dipende dal timbro
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
                self.colour = colours['light_blue']
            elif self.timbre == "ASax":
                self.colour = colours['orange']
            # Ottoni
            elif self.timbre == "Hn":
                self.colour = colours['purple']

            # Strumenti a tastiera e altri strumenti (se usati in futuro)
            else:
                self.colour = colours['green']  # Colore di default

    # method to save what the other robots have been played and save notes into a structure.
    def update_orchestra_spartito(self, full_spartito, millisecond, stimuli):
        if full_spartito is None or len(full_spartito) == 0:
            return  # Non aggiorna se lo spartito è vuoto
        # I store all the infos about the other robots.
        self.orchestra_spartito.append([entry for entry in full_spartito if entry["musician"] != self.number])
        
        if self.orchestra_spartito:
            # HARMONY MODULE
            self.update_note()
            # PHASE MODULE
            self.update_phase_kuramoto_model(millisecond)
            # BEAT MODULE
            self.update_beat_firefly(millisecond)
            # TIMBRE MODULE
            self.choose_timbre(stimuli)
    
    # method to update beat with firefly algorithm.
    def update_beat_firefly(self,millisecond):
        # Trova tutti gli eventi con dynamic == 'ff'
        ff_entries = [entry for sublist in self.orchestra_spartito 
              for entry in sublist 
              if entry["ms"] == millisecond and entry["dynamic"] == "ff"]
        
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
    
    # method to print thresholds history.
    def print_threshold_history(self, base_folder_path):
        # crea sottocartella thresholds se non esiste
        thresholds_dir = os.path.join(base_folder_path, "thresholds")
        os.makedirs(thresholds_dir, exist_ok=True)
        
        threshold_history = np.array(self.timbre_threshold_history)
        
        plt.figure(figsize=(10, 5))
        for i in range(self.num_timbres):
            plt.plot(threshold_history[:, i], label=f'Indiv {self.number + 1} - Task {i+1}')
        
        plt.xlabel("Time")
        plt.ylabel("Threshold")
        plt.title(f"Threshold Evolution for Robot {self.number + 1} with {self.num_timbres} tasks")
        plt.legend()
        # salva il grafico
        filename = f"robot_{self.number + 1}_thresholds.png"
        save_path = os.path.join(thresholds_dir, filename)
        plt.savefig(save_path)

        plt.close()





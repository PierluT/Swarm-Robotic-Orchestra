import matplotlib
import math
import rtmidi
import numpy as np
import time
import random
from datetime import timedelta
from classes.file_reader import File_Reader
from classes.tempo import Note
from classes.MIDIMessage import MIDIMessage
from classes.dictionaries import colours

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()
midi_sender = MIDIMessage()

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
        # variables form module 1
        self.phase = np.random.uniform(0, 2 * np.pi)
        self.clock_frequency = 0.25
        self.K = 1
        self.T = timedelta(milliseconds = 4000)
        #self.neighbours = []
        # buffers for incoming and emmiting messages. 
        self.recieved_message = []
        self.forwarded_message = []
        #self.comunication_interval = 0
        self.playing_flag = False
        self.crossed_zero_phase = False
        self.rotation_time = values_dictionary['rotation_time']
        self.change_direction_counter = time.time() + self.rotation_time
        #self.status = set()

    # Methods to manage robot status.
    def add_status(self, state):
        self.status.add(state)
        #print(f"Robot {self.number} entra nello stato: {state}")

    def remove_status(self, state):
        self.status.discard(state)
        #print(f"Robot {self.number} esce dallo stato: {state}")

    def has_status(self, state):
        return state in self.status

    def __repr__(self):
        return f"Robot(number={self.number}, coordinate x={self.x}, phase={self.phase.phi_i})"
    
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
        
        return (self.x, self.y), (end_x, end_y)
   
    def message_listener(self):
        if self.recieved_message and self.forwarded_message:
            #print("r: "+str(self.number)+" has recieved a message")
            #print(" | ".join(map(str, self.recieved_message)))
            #print()
            #print("r. send this message: "+str(self.number))
            #print(" | ".join(map(str, self.forwarded_message)))
            #print()
            # Itera attraverso la lista per accedere ai valori della fase
            for message in self.recieved_message:
                phase_value = message['phase']
                #print(f"Phase value: {phase_value}")
                self.update_phase_kuramoto_model(phase_value)

    def clean_buffers(self):
        self.forwarded_message.clear()
        self.recieved_message.clear()
    
    # manage differently the collision
    def change_direction_x_axes(self):
        self.change_direction_counter = time.time() + self.rotation_time
        self.vx = -self.vx
             
    def change_direction_y_axes(self):
        self.change_direction_counter = time.time() + self.rotation_time
        self.vy = -self.vy
    
    #return angle direction in rad.
    def get_angle(self):
        return math.atan2(self.vx,self.vy)
    
    def change_direction(self):
        self.vx = -self.vx
        self.vy = -self.vy

    def moveRobot(self): 
        if time.time() >= self.change_direction_counter:
            self.stop_and_rotate()
            self.change_direction_counter = time.time() + self.rotation_time

        self.x += self.vx
        self.y += self.vy
        
        # verify collision in x and y coordinates
        if self.x - self.radar_radius <= 10 or self.x + self.radar_radius  >= self.rectangleArea_width - 10 :
            self.change_direction_x_axes()
        if self.y - self.radar_radius <= 10 or self.y + self.radar_radius >= self.rectangleArea_heigth - 10 :
            self.change_direction_y_axes() 
    
    # INTRODUCE RANDOMNESS. 80% STOP FOR 2 SECONDS. 10% for 1 second. 
    
    # introduce kind of probabilites.
    def stop_and_rotate(self):
        # print("r. "+str(self.number)+ "si ferma e ruota")
        # to stop the robot
        # self.vx, self.vy = 0, 0
        #random rotation angle
        angle_degrees = random.uniform(0,360)
        angle_radians = math.radians(angle_degrees)
        # new velocity components
        self.vx = self.velocity * math.cos(angle_radians)
        self.vy = self.velocity * math.sin(angle_radians)

    # method to change color of the robot when interaction happens.
    def change_color(self):
        if self.crossed_zero_phase:
            self.colour = colours['blue']
        else:
            self.colour = colours['green']
    
    def set_emitter_message(self):
        
        entry = {
            "robot number": self.number,
            "phase": float(self.phase)
        }
        self.forwarded_message.append(entry)
    
    # to control if phase has crossed 2pi.
    def is_in_circular_range(self):
        return self.phase >= 0 and self.phase <= 0.09  
    
    # method to update internal robot phase.
    # What is the time gap between a call of update phase and another?
    def update_phase(self):
        #milliseconds = self.T.total_seconds() * 1000  
        # step = (2 * np.pi / self.T.total_seconds())  
        # phase += step 
        self.phase += (2 * np.pi / 4000)
        # normalization only if I reach 2pi then I go to 0.
        self.phase %= (2 * np.pi)
        # put a flag to control if previously you were near 2pi.
        if self.is_in_circular_range():
            self.crossed_zero_phase = True
        else:
            self.crossed_zero_phase = False
        
        # CONTROL THAT THE STEP IS ABOUT 1 MS.
   
    def update_phase_kuramoto_model(self,recieved_phase):
        self.phase += self.K * np.sin(recieved_phase - self.phase)
        # normalization
        self.phase %= (2 * np.pi)  
    
    # method to play the note.
    def play_note(self):
        
        if self.playing_flag:
            print(" suono!!!!")
            note_to_play = Note()
            midi_sender.send_MIDI_Message(note_to_play)
            self.playing_flag = False

    # robot updates itself in terms of position and phase.
    def step(self):
        # method to move itself.
        self.moveRobot()
        self.update_phase()
        self.message_listener()
        self.change_color()
"""""
    def play_note(self):
        note = Note()
"""



          

        
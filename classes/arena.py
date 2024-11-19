import ast
import numpy as np
import cv2
import csv
import time
from classes.file_reader import File_Reader
from collections import defaultdict

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Arena:

    def __init__(self):
        self. width = values_dictionary['width_arena']
        self.height = values_dictionary['height_arena']
        self.arena = np.zeros((self.height, self.width, 3), np.uint8)
        self.robot_data = defaultdict(list)
        self.draw_robots_time = []

    def show_arena(self,window_name = "Robot Simulation"):
        cv2.imshow(window_name, self.arena)
        # Usa cv2.waitKey con un breve ritardo per permettere l'aggiornamento continuo
        if cv2.waitKey(1) & 0xFF == ord('q'):
        # Esci dal programma se viene premuto il tasto 'q'
            cv2.destroyAllWindows()
            exit()

    def load_robot_data(self,filename):
        self.robot_data.clear()
        # read data from csv file
        with open(filename, mode='r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Salta l'intestazione
            for row in reader:
                millisecond, robot_number, x, y,compass, phase, colour_str, _ = row
                colour_str = colour_str.strip().strip('()')  # Rimuove parentesi e spazi extra
                colour = tuple(map(int, colour_str.split(',')))
                
                # Parsing del compasso
                if compass:
                        # Rimuovi spazi inutili e utilizza ast.literal_eval
                        compass_str_clean = compass.strip()
                        compass = ast.literal_eval(compass_str_clean)
                        start_point = tuple(map(float, compass[0]))
                        end_point = tuple(map(float, compass[1]))
                robot_info = {
                    "millisecond": int(millisecond),
                    "robot_number": int(robot_number),
                    "x": float(x),
                    "y": float(y),
                    "compass": (start_point, end_point),
                    "phase": phase,
                    "colour": colour
                }  
                self.robot_data[int(millisecond)].append(robot_info)

    def print_robot_data(self):
        for millisecond, robots in self.robot_data.items():
            print(f" Millisecond {millisecond}:")
            for robot in robots:
                print(f"  Robot: {robot['robot_number']}, "
                    f"X: {robot['x']}, Y: {robot['y']}, "
                    f"Phase: {robot['phase']}, Colour: {robot['colour']}")
    
    def draw_all_robots(self):
        # here is more than a 1ms. Measure that to know how fatser you can draw.
        # If you need 10 ms to draw then you have to recall function every 10 ms.
        # the time of changing colour and phase cross must be the same.
        # how many pictures do you want per second? 2o frames /s should be enough.
        for millisecond,robots in self.robot_data.items():
            self.arena.fill(0)
            
            for robot in robots:
                # I record the time before drawing a robot
                start_time = time.time()           
                self.draw_robot(robot)
                #I record the time after I drew it. 
                end_time = time.time()
                draw_time = end_time - start_time
                self.draw_robots_time.append(draw_time)

            self.show_arena("Robot Simulation")
            # I print the average of time spent to draw each robot.
            average_time = sum(self.draw_robots_time) / len(self.draw_robots_time)
            print(f"Tempo medio per disegnare un robot: {average_time:.6f} secondi")
            

    def draw_robot(self,robot):
        #print(f"robot  numero: {robot.number}, Velocità X: {robot.vx}, Velocità Y: {robot.vy}")
        cv2.circle(self.arena, (int(robot['x']), int(robot['y'])), values_dictionary['radius'], robot['colour'], -1)
        #cv2.circle(self.arena, (int(robot.x), int(robot.y)), robot.radar_radius, robot.colour)
        start_point, end_point = robot['compass']
        start_point = (int(start_point[0]), int(start_point[1]))
        end_point = (int(end_point[0]), int(end_point[1]))
        cv2.line(self.arena, start_point, end_point, (255, 255, 255), 2)  # Linea bianca per l'orientamento
        
        # add a label for the number of the robot
        label_position = (int(robot['x']) - 10, int(robot['y']) - values_dictionary['radius'] - 10)  # Regola la posizione sopra il robot
        cv2.putText(self.arena, str(robot['robot_number']), label_position, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)  # Testo bianco con spessore 2
   
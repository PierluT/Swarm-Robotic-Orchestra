import numpy as np
import cv2
import csv
from classes.file_reader import File_Reader

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Arena:

    def __init__(self):
        self. width = values_dictionary['width_arena']
        self.height = values_dictionary['height_arena']
        self.arena = np.zeros((self.height, self.width, 3), np.uint8)
        #self.robot_data = []

    def show_arena(self,window_name = "Robot Simulation"):
        cv2.imshow(window_name, self.arena)
        # Usa cv2.waitKey con un breve ritardo per permettere l'aggiornamento continuo
        if cv2.waitKey(1) & 0xFF == ord('q'):
        # Esci dal programma se viene premuto il tasto 'q'
            cv2.destroyAllWindows()
            exit()

    def load_robot_data(self,filename):
        robot_data = []
        # read data from csv file
        with open(filename, mode='r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Salta l'intestazione
            for row in reader:
                 millisecond, robot_number, x, y, phase, colour_str, _ = row
                 colour_str = colour_str.strip().strip('()')  # Rimuove parentesi e spazi extra
                 colour = tuple(map(int, colour_str.split(',')))
                 robot_data.append({
                    "millisecond": int(millisecond),
                    "robot_number": int(robot_number),
                    "x": float(x),
                    "y": float(y),
                    "phase": phase,
                    "colour": colour
                })
        return robot_data


    def draw_robot(self,robot):
        #print(f"robot  numero: {robot.number}, Velocità X: {robot.vx}, Velocità Y: {robot.vy}")
        cv2.circle(self.arena, (int(robot.x), int(robot.y)), robot.radius, robot.colour, -1)
        #cv2.circle(self.arena, (int(robot.x), int(robot.y)), robot.radar_radius, robot.colour)
        start_point, end_point = robot.compute_robot_compass()
        start_point = (int(start_point[0]), int(start_point[1]))
        end_point = (int(end_point[0]), int(end_point[1]))
        cv2.line(self.arena, start_point, end_point, (255, 255, 255), 2)  # Linea bianca per l'orientamento

        # add a label for the number of the robot
        label_position = (int(robot.x) - 10, int(robot.y) - robot.radius - 10)  # Regola la posizione sopra il robot
        cv2.putText(self.arena, str(robot.number), label_position, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)  # Testo bianco con spessore 2
""""
        # Aggiungi un'etichetta per la fase (theta) in radianti
        phase_label = f" phi: {robot.phase:.2f} rad"  # Formatta theta con due decimali e aggiungi "rad"
        phase_label_position = (int(robot.x) - 10, int(robot.y) - robot.radius - 30)  # Regola la posizione per theta
        cv2.putText(self.arena, phase_label, phase_label_position, 
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)  # Testo bianco con spessore 2
"""
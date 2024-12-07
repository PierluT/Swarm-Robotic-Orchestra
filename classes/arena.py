import ast
import numpy as np
import cv2
import subprocess
import os
import pygame
import csv
import time
from classes.file_reader import File_Reader
from collections import defaultdict

file_reader_valuse = File_Reader()
values_dictionary = file_reader_valuse.read_configuration_file()

class Arena:

    def __init__(self):
        self.width = values_dictionary['width_arena']
        self.height = values_dictionary['height_arena']
        self.arena = np.zeros((self.height, self.width, 3), np.uint8)
        self.robot_data = defaultdict(list)
        self.draw_robots_time = []
        self.frame_counter = 0
        self.png_folder = os.path.abspath("C://Users//pierl//Desktop//MMI//tesi//robotic-orchestra//png")

    def show_arena(self,window_name = "Robot Simulation"):
        cv2.imshow(window_name, self.arena)
        # Usa cv2.waitKey con un breve ritardo per permettere l'aggiornamento continuo
        if cv2.waitKey(1) & 0xFF == ord('q'):
        # Esci dal programma se viene premuto il tasto 'q'
            cv2.destroyAllWindows()
            exit()
    
    def save_arena_as_png(self):
        """Salva un frame dell'arena come PNG con nomi compatibili con FFmpeg."""
        filename = os.path.join(self.png_folder, f"frame{self.frame_counter:04d}.png")
        cv2.imwrite(filename, self.arena)
        #print(f"Salvato frame: {filename}")
        self.frame_counter += 1
    
    def load_robot_data(self,filename):
        self.robot_data.clear()
        # read data from csv file
        with open(filename, mode='r') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Salta l'intestazione
            for row in reader:
                millisecond, robot_number, x, y,compass, phase, colour_str,status= row
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

    def create_video(self, output_path="video.mp4", fps=33):
        """Crea un video dai file PNG usando FFmpeg."""
        try:
            # Comando FFmpeg per creare il video
            command = [
                "ffmpeg",
                "-y",  # Sovrascrivi il file di output se esiste
                "-framerate", str(fps),  # Frame per secondo
                "-i", os.path.join(self.png_folder, "frame%04d.png"),  # Pattern per i frame
                "-pix_fmt", "yuv420p",  # Formato pixel compatibile con i player
                output_path
            ]

            # Esegui FFmpeg
            subprocess.run(command, check=True)
            print(f"Video creato con successo: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante la creazione del video: {e}")
    
    def print_robot_data(self):
        for millisecond, robots in self.robot_data.items():
            print(f" Millisecond {millisecond}:")
            for robot in robots:
                print(f"  Robot: {robot['robot_number']}, "
                    f"X: {robot['x']}, Y: {robot['y']}, "
                    f"Phase: {robot['phase']}, Colour: {robot['colour']}")
    
    def draw_all_robots(self):  
        for millisecond,robots in self.robot_data.items():
            self.arena.fill(0)
            start_time = time.perf_counter()            
            for robot in robots:
                    self.draw_robot(robot)
            #I record the time after I drew them. 
            self.show_arena("Robot Simulation")
            end_time = time.perf_counter()
            draw_time = end_time - start_time
            self.draw_robots_time.append(draw_time)
            #if int(millisecond) % 30 == 0:
            self.save_arena_as_png()
            
            # I print the average of time spent to draw each robot.
            #print(f"Tempo per disegnare un frame: {draw_time*1000:.6f} ms")
        average_time = sum(self.draw_robots_time) / len(self.draw_robots_time)
        print(f" Tempo medio per disegnare un frame: {average_time*1000:.6f} ms" )

    
    
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
   
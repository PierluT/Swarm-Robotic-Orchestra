import ast
import numpy as np
import cv2
import subprocess
import sys
import os
from pathlib import Path
import csv
import pandas as pd
import shutil
from collections import defaultdict
from configparser import ConfigParser
config = ConfigParser()
config.read('configuration.ini')

class Arena:

    def __init__(self):
        self.width = int(config['PARAMETERS']['width_arena'])
        self.height = int(config['PARAMETERS']['height_arena'])
        self.arena = np.ones((self.height, self.width, 3), dtype=np.uint8) * np.array([200, 220, 240], dtype=np.uint8)
        self.robot_data = defaultdict(list)
        self.frame_counter = 0
        self.png_folder = "png"   

    def clean_png_folder(self):

        # 🔽 Crea la cartella se non esiste
        os.makedirs(self.png_folder, exist_ok=True)

        for filename in os.listdir(self.png_folder):
            file_path = os.path.join(self.png_folder, filename)
            try:
                # Rimuovi file o directory
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Rimuove file o link simbolici
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Rimuove directory
                #print(f"Rimosso: {file_path}")
            except Exception as e:
                print(f"Errore eliminando {file_path}: {e}")

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
    
    def load_robot_data(self,filename, simulation_number):
        #self.robot_data.clear()
        print("nome del file:"+ filename)
        #print(os.path.abspath(filename))
        # read data from csv file
        with open(filename, mode='r') as file:
            reader1 = csv.reader(file, delimiter=';')
            next(reader1)
            for row in reader1:
                simulation_number, millisecond, robot_number, x, y,compass, beat_phase, beat_counter,dynamic, colour_str, midinote, pitch, timbre, delay, playing_flag = row
                
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
                    "simulation number": simulation_number,
                    "millisecond": int(millisecond),
                    "robot_number": int(robot_number),
                    "x": float(x),
                    "y": float(y),
                    "compass": (start_point, end_point),
                    "phase": beat_counter,
                    "colour": colour
                } 

                self.robot_data[int(millisecond)].append(robot_info)
    
    def write_robot_data(self, writer,simulation_number, millisecond, robot):

        writer.writerow([
        
            simulation_number,
            millisecond, 
            robot.number, 
            robot.x, 
            robot.y,
            robot.compass, 
            robot.beat_phase, 
            robot.beat_counter,
            #robot.playing_flag,
            #robot.triggered_playing_flag,
            robot.note.dynamic,
            robot.colour,
            robot.note.midinote,
            robot.note.pitch,
            robot.timbre,
            robot.delay,
            robot.playing_flag
            #robot.harmony
    ])

    def open_video_file(self,filepath):
        if sys.platform.startswith('darwin'):
            # macOS
            subprocess.run(["open", filepath])
        elif sys.platform.startswith('win'):
            # Windows
            os.startfile(filepath)  # This only works on Windows
        elif sys.platform.startswith('linux'):
            # Linux (GNOME, KDE, etc.)
            subprocess.run(["xdg-open", filepath])
        else:
            print(f"Opening files is not supported on this OS via script. Please open {filepath} manually.")


    def create_video(self, output_path="video.mp4", fps=25, audio_path= None, auto_open=False):
        """
        Create a video from PNG images and optionally merge the provided audio.

        :param output_path:    Name/path of the output video file (e.g. "video.mp4").
        :param fps:            Frames per second for the resulting video.
        :param audio_path:     Path to a WAV/MP3/etc. file to merge as the audio track.
                               If None, no audio is added.
        """
        try:
                # Base FFmpeg command to convert PNG frames to a video
                command = [
                    "ffmpeg",
                    "-y",  # Overwrite output if it exists
                    "-framerate", str(fps),
                    "-i", os.path.join(self.png_folder, "frame%04d.png"),  # Input PNG frames
                ]

                # If audio is provided, add it to the command
                if audio_path:
                    
                    command.extend([
                        "-i", audio_path,  # Add the audio input
                        "-c:v", "libx264",  # Encode video with libx264
                        "-c:a", "aac",  # Encode audio with AAC
                        "-shortest",  # End when the shortest stream ends
                    ])
                else:
                    # If no audio, still need to encode video
                    command.extend([
                        "-pix_fmt", "yuv420p",  # Pixel format for compatibility
                        "-c:v", "libx264"
                    ])

                # Always output YUV420p for wide compatibility
                if audio_path:
                    command.extend(["-pix_fmt", "yuv420p"])

                # Specify the output file at the end
                command.append(output_path)

                # Run the FFmpeg command
                subprocess.run(command, check=True)
                print(f"Video successfully created: {output_path}")

                if auto_open:
                    self.open_video_file(output_path)

        except subprocess.CalledProcessError as e:
                print(f"Error during video creation: {e}")
    
    def draw_all_robots(self):
        for millisecond,robots in self.robot_data.items():
            self.arena.fill(255)           
            for robot in robots:
                self.draw_robot(robot)
            self.save_arena_as_png()
  
    def draw_robot(self,robot):
        #print(f"robot  numero: {robot.number}, Velocità X: {robot.vx}, Velocità Y: {robot.vy}")
        cv2.circle(self.arena, (int(robot['x']), int(robot['y'])), int(config['PARAMETERS']['radius']), robot['colour'], -1)
        #cv2.circle(self.arena, (int(robot.x), int(robot.y)), robot.radar_radius, robot.colour)
        start_point, end_point = robot['compass']
        start_point = (int(start_point[0]), int(start_point[1]))
        end_point = (int(end_point[0]), int(end_point[1]))
        cv2.line(self.arena, start_point, end_point, (255, 255, 255), 2)  # Linea bianca per l'orientamento
        
        # add a label for the number of the robot
        label_position = (int(robot['x']) - 10, int(robot['y']) - int(config['PARAMETERS']['radius']) - 10)  # Regola la posizione sopra il robot
        cv2.putText(self.arena, str(robot['robot_number']), label_position, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)  # Testo nero con spessore 2

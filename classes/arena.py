import ast
import numpy as np
import cv2
import subprocess
import sys
import os
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
        self.png_folder = "classes/png"

    
    def clear_png_folder(self):
        """Elimina tutti i file nella cartella PNG."""
        if not os.path.exists(self.png_folder):
            os.makedirs(self.png_folder)  # Crea la cartella se non esiste
        else:
            # Elimina tutti i file nella cartella
            for filename in os.listdir(self.png_folder):
                file_path = os.path.join(self.png_folder, filename)
                try:
                    if os.path.isfile(file_path):  # Controlla che sia un file
                        os.unlink(file_path)  # Cancella il file
                except Exception as e:
                    print(f"Errore nell'eliminazione del file {file_path}: {e}")       

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
                millisecond, robot_number, x, y,compass, phase, colour_str,status, midinote, pitch, timbre, delay = row
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

    def write_robot_data(self, writer, millisecond, robot):
        # add info for midinote and window to plot info about consensous
        writer.writerow([
        millisecond, 
        robot.number, 
        robot.x, 
        robot.y,
        robot.compass, 
        robot.phase, 
        robot.colour,
        robot.moving_status,
        robot.note.midinote,
        robot.note.pitch,
        robot.timbre,
        robot.delay
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


    def create_video(self, output_path="video.mp4", fps=25, audio_path=None, auto_open=False):
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
    
    # method to print robot data that have to bechecked.
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
            # I record the time after I drew them. 
            #self.show_arena("Robot Simulation")
            end_time = time.perf_counter()
            draw_time = end_time - start_time
            self.draw_robots_time.append(draw_time)
            # if int(millisecond) % 30 == 0:
            self.save_arena_as_png()
            
            # I print the average of time spent to draw each robot.
            # print(f"Tempo per disegnare un frame: {draw_time*1000:.6f} ms")
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
   
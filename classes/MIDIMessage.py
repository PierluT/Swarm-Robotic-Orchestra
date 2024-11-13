import time
import mido
import csv
from classes.tempo import Note
class MIDIMessage():
    
    def __init__(self):
        self.MIDI_Port_name = 'loopMIDI Port 1'
        self.music_csv_file = "music_data.csv"

    def read_data_from_csv_and_write_music_data(self, filename):
        with open(filename, mode= 'r') as file:
            reader = csv.reader(file,delimiter = ";")
            next(reader)
            
            with open(self.music_csv_file, mode = "w", newline = "") as output_file:
                writer = csv.writer(output_file, delimiter=";")
                writer.writerow(["ms", "musician", "note", "dur", "amp"])

                for row in reader:
                    millisecond = row[0]  # "ms"
                    robot_number = row[1]  # "robot number"
                    playing_flag = row[6]
                    if playing_flag == "True":
                        note = Note()
                        writer.writerow([millisecond, robot_number, note.midinote, note.dur, note.amp])
                        #print("robot n.:"+str(robot_number)+" deve suonare a ms: "+str(millisecond))


    
    def send_MIDI_Message(self,note_to_play):
         # Create MIDI output
        with mido.open_output(self.MIDI_Port_name) as outport:
            #print(f"Connessione aperta su {self.MIDI_Port_name}")
            message_on = mido.Message('note_on', note = note_to_play.midinote, velocity=120)
            message_off = mido.Message('note_off', note = note_to_play.midinote, velocity=120)
            outport.send(message_on)
            print(f"Message 'note_on' sent for note 60")                
            time.sleep(0.5)                
            outport.send(message_off)
            print(f"Messagge 'note_off' sent for note 60")

        
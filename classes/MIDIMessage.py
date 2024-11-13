import time
import mido
import csv
from mido import Message, MidiFile, MidiTrack, bpm2tempo
from classes.tempo import Note
class MIDIMessage():
    
    def __init__(self):
        self.MIDI_Port_name = 'loopMIDI Port 1'
        self.music_csv_file = "music_data.csv"
        self.midi_file = 'final_output.midi'

    def read_data_from_csv_and_write_music_data(self, filename):
        with open(filename, mode= 'r') as file:
            reader = csv.DictReader(file,delimiter = ";")
            next(reader)
            
            with open(self.music_csv_file, mode = "w", newline = "") as output_file:
                writer = csv.writer(output_file, delimiter=";")
                writer.writerow(["ms", "musician", "note", "dur", "amp", "bpm"])

                for row in reader:
                    millisecond = row["ms"]  # "ms"
                    robot_number = row["robot number"]  # "robot number"
                    playing_flag = row["is playing"]
                    
                    if playing_flag == "True":
                        note = Note()
                        writer.writerow([millisecond, robot_number, note.midinote, note.dur, note.amp, note.BPM])
                        #print("robot n.:"+str(robot_number)+" deve suonare a ms: "+str(millisecond))

    def convert_csv_to_midi(self):
        midi = MidiFile()
        track = MidiTrack()
        midi.tracks.append(track)

        previous_time_us = 0
        
        with open(self.music_csv_file, 'r') as f:
            reading_music_data = csv.DictReader(f, delimiter = ";")
            for row in reading_music_data:
                #print(row)
                time_ms = int(row['ms'])
                # time conversion from millisecond into microseconds.
                time_us = time_ms * 1000
                note = int(row['note'])
                duration_ms = int(row['dur'])
                # time conversion from millisecond into microseconds.
                duration_us = duration_ms * 1000
                amplitude = int(row['amp']) * 127
                bpm = int(row['bpm'])

                # then I compute us for tick
                ppq = 480
                # time in us for ppq
                tempo  = bpm2tempo(bpm)
                microseconds_per_tick = tempo / ppq
                # Compute numbers of tick in 1 second.
                ticks_per_second = int(1_000_000 / microseconds_per_tick)  

                # time that lasts from an event to another
                delta_time_us = time_us - previous_time_us
                # tick conversion
                delta_time_ticks = int(delta_time_us / 1000)  
                previous_time_us = time_us

                # Create event note on
                track.append(Message('note_on', note = note, velocity = 64, time = delta_time_ticks))

                # Create event note off after specified time.
                note_off_ticks = int(duration_us / 1000)
                
                track.append(Message('note_off', note=note, velocity=0, time = ticks_per_second ))

        # Salva il file MIDI
        midi.save(self.midi_file)
    
    def read_midi_file(self):
        midifile = MidiFile(self.midi_file)
        for i, track in enumerate(midifile.tracks):
            print(f"Track {i}: {track.name}")
            for msg in track:
                # Stampa ogni messaggio
                print(msg)


        
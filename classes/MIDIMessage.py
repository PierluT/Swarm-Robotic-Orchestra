import time

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
            reading_music_data = csv.DictReader(f, delimiter=";")
            for row in reading_music_data:
                # Leggi i valori dal CSV
                time_ms = int(row['ms'])
                time_us = time_ms * 1000  # Conversione millisecondi in microsecondi
                note = int(row['note'])
                duration_ms = int(row['dur'])
                duration_us = duration_ms * 1000  # Conversione millisecondi in microsecondi
                amplitude = int(float(row['amp']) * 127)  # Amplitude scalata a valori MIDI (0-127)
                bpm = int(row['bpm'])

                # Calcolo del tempo MIDI
                ppq = 480  # Pulses per Quarter Note
                tempo = bpm2tempo(bpm)  # Tempo in microsecondi per quarter note
                microseconds_per_tick = tempo / ppq  # Microsecondi per tick
                ticks_per_second = int(1_000_000 / microseconds_per_tick)

                # Delta time in tick (tra questo evento e il precedente)
                delta_time_us = time_us - previous_time_us
                delta_time_ticks = int(delta_time_us / microseconds_per_tick)
                previous_time_us = time_us

                # Durata della nota in tick
                duration_ticks = int(duration_us / microseconds_per_tick)

                # Crea gli eventi MIDI
                track.append(Message('note_on', note=note, velocity=amplitude, time=delta_time_ticks))
                track.append(Message('note_off', note=note, velocity=amplitude, time=duration_ticks))

        # Salva il file MIDI
        midi.save(self.midi_file)


    
    def read_midi_file(self):
        midifile = MidiFile(self.midi_file)
        for i, track in enumerate(midifile.tracks):
            print(f"Track {i}: {track.name}")
            for msg in track:
                # Stampa ogni messaggio
                print(msg)
    
    def midi_event(self,filename):
        self.read_data_from_csv_and_write_music_data(filename)
        self.convert_csv_to_midi()
        self.read_midi_file()


        
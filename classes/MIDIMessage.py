import time
import mido
#from classes.phase_module import Phase_Module

#phase_module = Phase_Module()
class MIDIMessage():
    
    def __init__(self):
        self.MIDI_Port_name = 'loopMIDI Port 1'


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

        
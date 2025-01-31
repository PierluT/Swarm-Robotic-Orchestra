import random

class Note:
    def __init__(self, midinote, bpm, duration):
         
         self.midinote = midinote
         # have to relate with the dynamics, ff mf e pp.
         self.amp = 1
         self.dur = duration
         self.bpm = bpm
         self.pitch = self.midinote % 12 
         self.octave = (self.midinote - 12) // 12
         self.dynamic = ""
    
    def __repr__(self):
        return "\n\t".join([ 
                                "midinote: %d"%self.midinote,
                                "pitch: %.1f"%self.pitch,
                                "octave: %d" % self.octave
                                ])
                                #"amplitude: %.1f"%self.amp

class TimeSignature:

    def __init__(self):
        # how many beats in a bar
        self.numerator_time_signature = [3]
        # duration of the bar. This value is related to the phase denominator.
        self.denominator_time_signature = [4]
        self.time_signature_combiantion = random.choice(self.get_time_signature_combinations())

    def get_time_signature_combinations(self):
        
        tempo_signatures = []
        for numerator in self.numerator_time_signature:
            for denominator in self.denominator_time_signature:
                # gives back a tuple where numerator and denominator are separated.
                tempo_signatures.append((numerator, denominator))
        
        return tempo_signatures

    


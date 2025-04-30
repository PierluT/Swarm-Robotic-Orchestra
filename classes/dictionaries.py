
colours = {
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'black': (0, 0, 0),
    'brown': (42, 42, 165),  
    'orange': (0, 165, 255),  
    'yellow': (0, 255, 255),
    'pink': (255, 192, 203),
    'purple': (128, 0, 128),
    'light_blue': (255, 200, 100),  # Azzurro chiaro
    'sky_blue': (255, 180, 70),     # Blu cielo
    'dark_blue': (139, 0, 0),       # Blu scuro
    'grey': (128, 128, 128)         # Grigio
}


major_scales = {
    
    0: [0, 2, 4, 5, 7, 9, 11],    # Do maggiore (C Major)
    1: [1, 3, 5, 6, 8, 10, 0],    # Do# maggiore (C# Major)
    2: [2, 4, 6, 7, 9, 11, 1],    # Re maggiore (D Major)
    3: [3, 5, 7, 8, 10, 0, 2],    # Re# maggiore (D# Major)
    4: [4, 6, 8, 9, 11, 1, 3],    # Mi maggiore (E Major)
    5: [5, 7, 9, 10, 0, 2, 4],    # Fa maggiore (F Major)
    6: [6, 8, 10, 11, 1, 3, 5],   # Fa# maggiore (F# Major)
    7: [7, 9, 11, 0, 2, 4, 6],    # Sol maggiore (G Major)
    8: [8, 10, 0, 1, 3, 5, 7],    # Sol# maggiore (G# Major)
    9: [9, 11, 1, 2, 4, 6, 8],    # La maggiore (A Major)
    10: [10, 0, 2, 3, 5, 7, 9],   # La# maggiore (A# Major)
    11: [11, 1, 3, 4, 6, 8, 10],  # Si maggiore (B Major)
}


major_pentatonic_scales = {
    0:  [0, 2, 4, 7, 9],     # C major pentatonic
    1:  [1, 3, 5, 8, 10],    # C# / Db major pentatonic
    2:  [2, 4, 6, 9, 11],    # D major pentatonic
    3:  [3, 5, 7, 10, 0],    # D# / Eb
    4:  [4, 6, 8, 11, 1],    # E major pentatonic
    5:  [5, 7, 9, 0, 2],     # F major pentatonic
    6:  [6, 8, 10, 1, 3],    # F# / Gb
    7:  [7, 9, 11, 2, 4],    # G major pentatonic
    8:  [8, 10, 0, 3, 5],    # G# / Ab
    9:  [9, 11, 1, 4, 6],    # A major pentatonic
    10: [10, 0, 2, 5, 7],    # A# / Bb
    11: [11, 1, 3, 6, 8],    # B major pentatonic
}

whole_tone_scales = {
    0:  [0, 2, 4, 6, 8, 10],    # C whole-tone
    1:  [1, 3, 5, 7, 9, 11],    # C# whole-tone
    2:  [2, 4, 6, 8, 10, 0],    # D whole-tone
    3:  [3, 5, 7, 9, 11, 1],    # D# whole-tone
    4:  [4, 6, 8, 10, 0, 2],    # E whole-tone
    5:  [5, 7, 9, 11, 1, 3],    # F whole-tone
    6:  [6, 8, 10, 0, 2, 4],    # F# whole-tone
    7:  [7, 9, 11, 1, 3, 5],    # G whole-tone
    8:  [8, 10, 0, 2, 4, 6],    # G# whole-tone
    9:  [9, 11, 1, 3, 5, 7],    # A whole-tone
    10: [10, 0, 2, 4, 6, 8],    # A# whole-tone
    11: [11, 1, 3, 5, 7, 9],    # B whole-tone
}

orchestra_to_midi_range = {

    "Strings": {
        # violin
        "Vn": list(range(55, 100)),      
        # viola
        "Va": list(range(48, 96)),         # C3–E6
        # violoncello
        "Vc": list(range(36, 84)),         # C2–E5
        # contrabbasso
        "Cb": list(range(28, 72))  # B0–B3
        #"Harp": list(range(24, 104))          # C1–G7
    },
    "Woodwinds": {
        # flute
        "Fl": list(range(59, 98)),         # B3–D7
        #"Piccolo": list(range(74, 109)),      # D5–C8
        # oboe
        "Ob": list(range(58, 92)),          # B3–G6
        #"English Horn": list(range(52, 85)),  # E3–C6
        # clarinet Bb
        "ClBb": list(range(52, 92)),      # E3–C7
        #"Bass Clarinet": list(range(38, 66)), # D2–F5
        # bassoon
        "Bn": list(range(34, 75)),       # B1–E5
        
    },
    "Brass": {
        # trumpet in C
        "TpC": list(range(54, 87)),            # F#3–D6
        # Trombone
        "Tbn": list(range(34, 73)),           # E2–F5
        #"Bass Trombone": list(range(36, 66)),      # C2–F4
        # horn
        "Hn": list(range(31, 77)),        # F2–F5
        # Bass tuba
        "BTb": list(range(30, 65))                # D1–F4
    },
    "Percussion": {
        #"Timpani": list(range(38, 61)),            # D2–C4
        #"Glockenspiel": list(range(79, 110)),      # G5–C8
        #"Xylophone": list(range(65, 97)),          # F3–C7
        #"Vibraphone": list(range(65, 90)),         # F3–F6
        #"Marimba": list(range(48, 97)),            # C2–C7
        #"Tubular Bells": list(range(60, 78)),      # C4–F5
        #"Bass Drum": [36],                         # Single note
        #"Snare Drum": [38],                        # Single note
        #"Tambourine": [39],                        # Single note
        #"Cymbals": [40],                           # Single note
        #"Triangle": [41]                           # Single note
    },
    "Keyboards": {
        #"Piano": list(range(21, 110)),             # A0–C8
        #"Organ": list(range(36, 97)),              # C2–C7
        #"Celesta": list(range(48, 97)),            # C3–C7
        #"Harpsichord": list(range(29, 90))         # F1–F6
    },
    "Other Instruments": {
        # alto sax
        "ASax": list(range(49, 81)),                # Bb3–F6
        "Acc": list(range(28, 109)),          # F2–C6
        #"Classical Guitar": list(range(40, 89)),   # E2–E6
        #"Mandolin": list(range(55, 101))           # G3–E7
    }
}

instrument_ensembles = {
    2: ["Vn", "Va"],
    3: ["Fl", "ClBb", "Vc"],
    4: ["TpC", "Hn", "Tbn", "Bn"],
    5: ["Ob", "Fl", "ClBb", "Bn", "Hn"],
    6: ["Vn", "Va", "Vc", "Cb", "Fl", "Ob"],
    7: ["TpC", "Tbn", "Hn", "BTb", "ClBb", "ASax", "Vc"],
    8: ["Vn", "Va", "Vc", "Cb", "Fl", "Ob", "ClBb", "Bn"],
    9: ["TpC", "Tbn", "Hn", "BTb", "Fl", "Ob", "ClBb", "Bn", "Acc"],
    10: ["Vn", "Va", "Vc", "Cb", "Fl", "Ob", "ClBb", "Bn", "TpC", "Acc"]
}








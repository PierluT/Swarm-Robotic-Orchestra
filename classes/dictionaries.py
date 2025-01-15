
colours = {
    'green': (0,255,0),
    'red':  (0,0,255),
    'blue': (255,0,0)
}

major_scales = {
    0: [0, 2, 4, 5, 7, 9, 11],    # Do maggiore (C Major)
    1: [1, 3, 5, 6, 8, 10, 0],    # Do# maggiore (C# Major)
    2: [2, 4, 6, 7, 9, 11, 1],    # Re maggiore (D Major)
    #3: [3, 5, 7, 8, 10, 0, 2],    # Re# maggiore (D# Major)
    4: [4, 6, 8, 9, 11, 1, 3],    # Mi maggiore (E Major)
    #5: [5, 7, 9, 10, 0, 2, 4],    # Fa maggiore (F Major)
    6: [6, 8, 10, 11, 1, 3, 5],   # Fa# maggiore (F# Major)
    7: [7, 9, 11, 0, 2, 4, 6],    # Sol maggiore (G Major)
    #8: [8, 10, 0, 1, 3, 5, 7],    # Sol# maggiore (G# Major)
    9: [9, 11, 1, 2, 4, 6, 8],    # La maggiore (A Major)
    #10: [10, 0, 2, 3, 5, 7, 9],   # La# maggiore (A# Major)
    #11: [11, 1, 3, 4, 6, 8, 10],  # Si maggiore (B Major)
}

orchestra_to_midi_range = {

    "Strings": {
        #"Violin": list(range(55, 104)),       # G3–A7
        #"Viola": list(range(48, 77)),         # C3–E6
        #"Cello": list(range(36, 65)),         # C2–E5
        #"Double Bass": list(range(28, 61)),   # E1–C4
        #"Harp": list(range(24, 104))          # C1–G7
    },
    "Woodwinds": {
        "Flute": list(range(59, 99)),         # B3–D7
        #"Piccolo": list(range(74, 109)),      # D5–C8
        "Oboe": list(range(50, 92)),          # B3–G6
        #"English Horn": list(range(52, 85)),  # E3–C6
        "Clarinet_Bb": list(range(52, 98)),      # E3–C7
        #"Bass Clarinet": list(range(38, 66)), # D2–F5
        #"Bassoon": list(range(35, 66)),       # B1–E5
        #"Contrabassoon": list(range(23, 60))  # B0–B3
    },
    "Brass": {
        "Trumpet": list(range(54, 87)),            # F#3–D6
        "Trombone": list(range(34, 73)),           # E2–F5
        #"Bass Trombone": list(range(36, 66)),      # C2–F4
        #"French Horn": list(range(41, 78)),        # F2–F5
        "Tuba": list(range(30, 66))                # D1–F4
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
        #"Saxophone": list(range(58, 90)),          # Bb3–F6
        #"Accordion": list(range(41, 85)),          # F2–C6
        #"Classical Guitar": list(range(40, 89)),   # E2–E6
        #"Mandolin": list(range(55, 101))           # G3–E7
    }
}

music_formations = {
    
    "String Quartet": [
        "Violin", "Violin", "Viola", "Cello"
    ],
    "Brass Decet": [
        "Trumpet", "Trumpet", "Trombone", "Trombone", "Bass Trombone", 
        "French Horn", "French Horn", "Tuba"
    ],
    "Piano and Cello": [
        "Piano", "Cello"
    ],
    "Piano and Trumpet": [
        "Piano", "Trumpet"
    ],
    "String Trio": [
        "Violin", "Viola", "Cello"
    ],
    "Woodwind Septet": [
        "Flute", "Oboe", "Clarinet", "Bassoon", "English Horn", 
        "Trumpet", "Tuba"
    ],
    "Brass Sextet": [
        "Trumpet", "Trumpet", "Trombone", "Trombone", "French Horn", "Tuba"
    ],
    "Chamber Orchestra": [
        "Violin", "Viola", "Cello", "Double Bass", "Flute", "Oboe", "Clarinet"
    ],
    "Symphony Orchestra": [
        "Violin", "Violin", "Viola", "Cello", "Double Bass", 
        "Flute", "Oboe", "Clarinet", "Bassoon", 
        "Trumpet", "Trumpet", "Trombone", "Trombone", "French Horn", "Tuba", 
        "Timpani", "Harp"
    ],
    "Big Band" : [
        "Trumpet", "Trumpet", "Trombone", "Trombone", "Saxophone", "Saxophone", 
        "Saxophone", "Saxophone", "Piano", "Bass", "Drums"
    ],
    "Wind Ensemble": [
        "Flute", "Oboe", "Clarinet", "Bassoon", "French Horn", "Trumpet", 
        "Trombone", "Tuba", "Percussion"
    ],
    "Trombone Quartet" : [
        "Trombone", "Trombone", "Bass Trombone", "Bass Trombone"
    ],
    "Trumpet Quartet" : [
        "Trumpet", "Trumpet", "Trumpet", "Trumpet"
    ],
    "French Horn Quartet": [
        "French Horn", "French Horn", "French Horn", "French Horn"
    ],
    "Percussion Ensemble" : [
        "Timpani", "Snare Drum", "Bass Drum", "Cymbals", "Tambourine", "Triangle"
    ],
    "Marimba-Vibraphone Duo" : [
        "Marimba", "Vibraphone"
    ],
    "Xylophone-Glockenspiel Duo" : [
        "Xylophone", "Glockenspiel"
    ],
    "Percussion Trio" : [
        "Timpani", "Marimba", "Snare Drum"
    ],
    "Orchestral Percussion Section" : [
        "Timpani", "Glockenspiel", "Xylophone", "Vibraphone", "Bass Drum", "Cymbals", "Tambourine", "Triangle"
    ],
    "Solo Percussion Performance" : [
        "Snare Drum", "Bass Drum", "Cymbals"
    ],
    "Marimba-Timpani Duo" : [
        "Marimba", "Timpani"
    ],
    "Percussion Quartet" : [
        "Snare Drum", "Bass Drum", "Xylophone", "Vibraphone"
    ],
    "Saxophone Quartet" : [
        "Saxophone", "Saxophone", "Saxophone", "Saxophone"
    ],
    "Accordion-Guitar Duo" : [
        "Accordion", "Classical Guitar"
    ],
    "Mandolin-Saxophone Duo" : [
        "Mandolin", "Saxophone"
    ],
    "Other Instruments Ensemble" : [
        "Saxophone", "Accordion", "Classical Guitar", "Mandolin"
    ],
    "Accordion Quartet" : [
        "Accordion", "Accordion", "Accordion", "Accordion"
    ],
    "Mandolin Quartet" : [
        "Mandolin", "Mandolin", "Mandolin", "Mandolin"
    ],
    "Guitar-Saxophone Duo" : [
        "Classical Guitar", "Saxophone"
    ],
    "Guitar-Mandolin Duo" : [
        "Classical Guitar", "Mandolin"
    ],
    "Marching Band" : [
        "Trumpet", "Trumpet", "Trombone", "Trombone", "French Horn", "Sousaphone", 
        "Snare Drum", "Bass Drum", "Cymbals", "Tambourine", "Timpani"
    ],
    "Piano and Violin": [
        "Piano", "Violin"
    ],
    "Piano and Viola": [
        "Piano", "Viola"
    ],
    "Piano and Cello": [
        "Piano", "Cello"
    ],
    "Piano and Flute": [
        "Piano", "Flute"
    ],
    "Piano and Clarinet": [
        "Piano", "Clarinet"
    ],
    "Piano and Trumpet": [
        "Piano", "Trumpet"
    ],
    "Piano and Trombone": [
        "Piano", "Trombone"
    ],
    "Piano and French Horn": [
        "Piano", "French Horn"
    ],
    "Piano and Saxophone": [
        "Piano", "Saxophone"
    ],
    "Piano and Accordion": [
        "Piano", "Accordion"
    ],
    "Piano and Classical Guitar": [
        "Piano", "Classical Guitar"
    ],
    "Piano and Mandolin": [
        "Piano", "Mandolin"
    ],
    "Swing Band": [
    "Trumpet", "Trumpet", "Trombone", "Trombone", "Saxophone", "Saxophone", 
    "Saxophone", "Saxophone", "Piano", "Bass", "Drums"
    ],
    "Baroque Orchestra": [
    "Violin", "Violin", "Viola", "Cello", "Double Bass", "Flute", "Oboe", 
    "Bassoon", "Trumpet", "French Horn", "Timpani", "Harpsichord"
    ],
    "Orchestra": [
    "Violin", "Violin", "Viola", "Cello", "Double Bass", "Flute", "Oboe", 
    "Clarinet", "Bassoon", "Trumpet", "Trombone", "French Horn", "Tuba", 
    "Timpani", "Harp", "Piano"
    ],
    "Bebop Band": [
    "Trumpet", "Saxophone", "Piano", "Double Bass", "Drums"
    ],
    "Gipsy Band": [
    "Violin", "Accordion", "Guitar", "Double Bass", "Drums"
    ]

}





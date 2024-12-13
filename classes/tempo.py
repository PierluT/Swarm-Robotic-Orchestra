import random

default_note_duration = {
    "m": 4, # semibreve
    "q": 1 # semiminima
}

metronome_grammar = {
    "M": ["q","q","q","q"]
}

# by now every 4/4 bar is formed by only semiminima.
ex_i_grammar={
    "S":["M", "SM"],
    "M": [["q","q","q","q"]],
}

def random_element_in_list(list_of_elements):
    return list_of_elements[random.randint(0,len(list_of_elements)-1)]

class Grammar_Sequence:
    def __init__(self, grammar):
        self.grammar=grammar
        self.grammar_keys=list(grammar.keys())
        self.N=len(self.grammar_keys)
        self.sequence=[]

    
    def replace(self, index, convert_to):
        """Replace symbol in index with symbol(s) in convert_to

        Parameters
        ----------
        index : int
            index of the sequence to replace
        convert_to : str, list of str
            symbol(s) to convert to
        """
        convert_to = [convert_to,] if type(convert_to)==str else convert_to
        begin_seq=self.sequence[:index]
        end_seq=self.sequence[index+1:] if (index+1)<len(self.sequence) else []
        self.sequence=begin_seq+convert_to+end_seq
    
    def convert_sequence(self, idxs):        
        """Convert a non-terminal symbol in the sequence

        Parameters
        ----------
        idxs : list of integers
            integers where non-terminal symbols are 
        """

        index = random_element_in_list(idxs)
        symbol=self.sequence[index]
        convert_to = random_element_in_list(self.grammar[symbol])
        self.replace(index, convert_to)
        
    def find_nonterminal_symbols(self, sequence):
        """Checks if there are still nonterminal symbols in a sequence
        and where they are

        Parameters
        ----------
        sequence : list of str
            sequence

        Returns
        -------
        list
            list of indices where nonterminal symbols are
        boolean
            True if there are nonterminal symbols
        """
        idxs=[]
        for s, symbol in enumerate(sequence):
            if symbol in self.grammar_keys:
                idxs.append(s) 
        return idxs, len(idxs)>0
    def create_sequence(self, start_sequence):
        """Create a sequence of terminal symbols 
        starting from a sequence of non-terminal symbols.
        While this could be done with recursive function, we use iterative approach

        Parameters
        ----------
        start_sequence : list of str
            the sequence of non-terminal symbols

        Returns
        -------
        list of str
            the final sequence of terminal symbols
        list of list of str
            the history of sequence modification from non-terminal to terminal symbols
        """
        self.sequence=start_sequence
        sequence_transformation=[start_sequence]
        while True:
            idxs, to_convert=self.find_nonterminal_symbols(self.sequence)
            if not to_convert:
                break
            self.convert_sequence(idxs)
            sequence_transformation.append(self.sequence.copy())
        return self.sequence, sequence_transformation
    
    def dividi_sequenza_ritmica_melodia(self,final_sequence):
        sequenza_divisa = []
        battuta = []
        tempo_battuta = 0

        # Calcolo durata nota in base alla grammatica  
        for simbolo in final_sequence:
            durata = default_note_duration.get(simbolo, 0)

            if tempo_battuta + durata > 4:
                sequenza_divisa.append(battuta)
                battuta = []
                tempo_battuta = 0

            battuta.append(simbolo)
            tempo_battuta += durata

        # Assicurati di aggiungere l'ultima battuta alla fine
        sequenza_divisa.append(battuta)
        print(sequenza_divisa)

        return sequenza_divisa


class Note:
    def __init__(self, midinote, id):
         self.id = id
         self.midinote = midinote
         self.amp = 1
         self.dur = 1
         self.bpm = 60
         self.MIDI_Port_name = 'loopMIDI Port 1'
    
    def __repr__(self):
        return "\n\t".join([ 
                                "midinote: %d"%self.midinote,
                                "id: %s"%str(self.id)])
                                #"amplitude: %.1f"%self.amp

                                
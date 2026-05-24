

class MusicTheory:
    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    SCALES = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    }
    
    CHORDS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dominant": [0, 4, 7, 10],
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "diminished": [0, 3, 6],
        "augmented": [0, 4, 8],
    }
    
    @staticmethod
    def GetNoteNumber(note_name: str, octave: int) -> int:
        try:
            note_index = MusicTheory.NOTES.index(note_name)
            return 12 * (octave + 1) + note_index
        except ValueError:
            return 60
    
    @staticmethod
    def GetNoteName(note_number: int) -> tuple[str, int]:
        octave = (note_number // 12) - 1
        note_index = note_number % 12
        return (MusicTheory.NOTES[note_index], octave)
    
    @staticmethod
    def GetScaleNotes(root_note: str, scale: str, octave: int, num_notes: int) -> list[int]:
        try:
            if scale not in MusicTheory.SCALES:
                scale = "major"
            
            scale_intervals = MusicTheory.SCALES[scale]
            root_number = MusicTheory.GetNoteNumber(root_note, octave)
            
            notes = []
            current_octave = octave
            
            for i in range(num_notes):
                scale_degree = i % len(scale_intervals)
                interval = scale_intervals[scale_degree]
                
                if i > 0 and scale_degree == 0:
                    current_octave += 1
                
                note = MusicTheory.GetNoteNumber(root_note, current_octave) + interval
                notes.append(note)
            
            return notes
        except Exception:
            return list(range(60, 60 + num_notes))
    
    @staticmethod
    def GetChordNotes(root_note: str, chord_type: str, octave: int) -> list[int]:
        try:
            if chord_type not in MusicTheory.CHORDS:
                chord_type = "major"
            
            chord_intervals = MusicTheory.CHORDS[chord_type]
            root_number = MusicTheory.GetNoteNumber(root_note, octave)
            
            notes = [root_number + interval for interval in chord_intervals]
            return notes
        except Exception:
            return [60, 64, 67]
    
    @staticmethod
    def IsValidNote(note_number: int) -> bool:
        return 0 <= note_number <= 127
    
    @staticmethod
    def ClampNote(note_number: int) -> int:
        return max(0, min(127, note_number))

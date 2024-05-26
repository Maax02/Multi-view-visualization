from collections import defaultdict
import mido


def get_midi_duration(file_path):
    mid = mido.MidiFile(file_path)
    
    tempo = 500000
    ticks_per_beat = mid.ticks_per_beat
    track_durations = []
    
    for i, track in enumerate(mid.tracks):
        current_time = 0.0
        for msg in track:
            delta_time_seconds = ticks_to_seconds(msg.time, tempo, ticks_per_beat)
            current_time += delta_time_seconds
            
            if msg.type == 'set_tempo':
                tempo = msg.tempo
        
        track_durations.append(current_time)
    
    total_duration = max(track_durations)
    return total_duration


def detect_chords(file_path):
    mid = mido.MidiFile(file_path)
    
    tempo = 500000
    ticks_per_beat = mid.ticks_per_beat
    current_time = 0.0
    
    active_notes = defaultdict(list)
    chords = []
    
    for i, track in enumerate(mid.tracks):
        for msg in track:
            delta_time_seconds = ticks_to_seconds(msg.time, tempo, ticks_per_beat)
            current_time += delta_time_seconds
            
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            elif msg.type == 'note_on' and msg.velocity > 0:
                active_notes[current_time].append(msg.note)
    
    for time, notes in active_notes.items():
        if len(notes) >= 3:
            normalized_notes = normalize_notes(notes)
            for i in range(len(normalized_notes)):
                root = normalized_notes[i]
                intervals = sorted([(note - root) % 12 for note in normalized_notes])
                if intervals[:3] == [0, 4, 7]:
                    chords.append((time, 'Major', notes))
                    break
                elif intervals[:3] == [0, 3, 7]:
                    chords.append((time, 'Minor', notes))
                    break
    
    return chords


def normalize_notes(notes):
    return sorted([note % 12 for note in notes])


def ticks_to_seconds(ticks, tempo, ticks_per_beat):
    # Convert ticks to microseconds
    microseconds = (ticks * tempo) / ticks_per_beat
    # Convert microseconds to seconds
    seconds = microseconds / 1_000_000
    return seconds


def parse_midi(file_path, output_file_path):
    # Open the MIDI file
    mid = mido.MidiFile(file_path)
    
    # Initial tempo (default 500000 microseconds per beat, which is 120 BPM)
    tempo = 500000
    
    # Current time in seconds
    current_time = 0.0
    
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    with open(output_file_path, 'w') as output_file:
        for i, track in enumerate(mid.tracks):
            output_file.write(f'Track {i}: {track.name}\n')
            for msg in track:
                # Convert delta time to seconds
                delta_time_seconds = ticks_to_seconds(msg.time, tempo, mid.ticks_per_beat)
                current_time += delta_time_seconds
                frame_number = int(current_time * 24)
                
                if msg.type == 'set_tempo':
                    # Update tempo when tempo change message is encountered
                    tempo = msg.tempo
                elif msg.type == 'note_on' and msg.velocity > 0:
                    # Write the note and its velocity along with the current time in seconds to the file
                    output_file.write(f'Note {msg.note} ({notes[msg.note % 12]})| velocity {msg.velocity} | tempo: {msg.time} | time: {current_time:.2f} seconds | frame: {frame_number} => Midi message: ({msg})\n')


midi_file_path = 'Fur Elise.mid'
output_file_path = 'parsed_MIDI.txt'

parse_midi(midi_file_path, output_file_path)

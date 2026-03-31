import pretty_midi
import numpy as np

def analyze_chords(midi_file):
    """Анализирует MIDI-файл и извлекает аккорды"""
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    
    all_notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            all_notes.append((note.pitch, note.start, note.end))
    
    chords = []
    processed = set()
    
    for i, (pitch, start, end) in enumerate(all_notes):
        if i in processed:
            continue
            
        current_chord = [pitch]
        processed.add(i)
        
        for j, (p2, s2, e2) in enumerate(all_notes):
            if j not in processed and abs(s2 - start) < 0.1:
                current_chord.append(p2)
                processed.add(j)
        
        if len(current_chord) >= 2:
            chords.append(sorted(current_chord))
    
    # Убираем дубликаты
    unique_chords = []
    for chord in chords:
        if not unique_chords or unique_chords[-1] != chord:
            unique_chords.append(chord)
    
    return unique_chords

def generate_bass(chords, style="rock", complexity=4):
    """Генерирует басовую партию"""
    bass_notes = []
    
    for chord in chords:
        if not chord:
            bass_notes.append((36, 1.0))
            continue
        
        root_note = min(chord)
        bass_root = root_note - 12
        
        if style == "simple":
            bass_notes.append((bass_root, 2.0))
            
        elif style == "rock":
            fifth = bass_root + 7
            for beat in range(complexity):
                pos = beat * (2.0 / complexity)
                if beat % 2 == 0:
                    bass_notes.append((bass_root, 0.4))
                else:
                    bass_notes.append((fifth, 0.4))
                    
        elif style == "funk":
            fifth = bass_root + 7
            octave = bass_root + 12
            pattern = [bass_root, fifth, bass_root, octave, bass_root, fifth, bass_root, octave]
            for i in range(min(complexity, len(pattern))):
                bass_notes.append((pattern[i], 0.3))
    
    return bass_notes

def create_bass_midi(bass_notes, tempo=120, output_path="bass_output.mid"):
    """Создает MIDI-файл с басовой партией"""
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    bass = pretty_midi.Instrument(program=33, name="Generated Bass")
    
    current_time = 0
    for note_num, duration in bass_notes:
        note = pretty_midi.Note(
            velocity=90,
            pitch=note_num,
            start=current_time,
            end=current_time + duration
        )
        bass.notes.append(note)
        current_time += duration
    
    midi.instruments.append(bass)
    midi.write(output_path)
    return output_path

def process_midi(input_file, style="rock", complexity=4, tempo=120):
    """Основная функция обработки с возвратом данных для визуализации"""
    chords = analyze_chords(input_file)
    if not chords:
        return None, "Не удалось найти аккорды в файле"
    
    bass_notes = generate_bass(chords, style, complexity)
    output_file = "bass_output.mid"
    create_bass_midi(bass_notes, tempo, output_file)
    
    # Возвращаем также данные об аккордах для визуализации
    return output_file, f"Успешно! Найдено {len(chords)} аккордов, сгенерировано {len(bass_notes)} нот баса", chords

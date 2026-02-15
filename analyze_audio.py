from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import sys
import os
from deep_translator import GoogleTranslator

# Global analyzer instance to avoid reloading model
_analyzer_instance = None
# Cache for translations to avoid repeated API calls
_translation_cache = {}

def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        print(f"Loading BirdNET model...")
        try:
            # Initialize without language parameter (it's not supported in this version)
            _analyzer_instance = Analyzer()
        except Exception as e:
            print(f"Error initializing BirdNET Analyzer: {e}")
            raise e
    return _analyzer_instance

def translate_bird_name(english_name: str) -> str:
    """Translates bird name from English to Chinese using Google Translate."""
    if english_name in _translation_cache:
        return _translation_cache[english_name]
    
    try:
        # Use deep_translator
        translator = GoogleTranslator(source='en', target='zh-CN')
        translated = translator.translate(english_name)
        
        # Cache the result
        if translated:
            _translation_cache[english_name] = translated
            return translated
    except Exception as e:
        print(f"Translation error for {english_name}: {e}")
    
    return english_name

def analyze_audio(file_path: str, lat: float = None, lon: float = None, min_conf: float = 0.25):
    """
    Analyzes the given audio file using BirdNET.
    Returns a list of detections with translated common names.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return []

    try:
        analyzer = get_analyzer()
    except Exception:
        return []

    # Configure the recording
    recording = Recording(
        analyzer,
        file_path,
        lat=lat,
        lon=lon,
        min_conf=min_conf,
    )

    # Run the analysis
    try:
        recording.analyze()
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return []

    # Post-process detections to add Chinese names
    for detection in recording.detections:
        original_name = detection['common_name']
        # Translate and update the common_name field directly or add a new one
        # Here we overwrite it for display purposes
        detection['common_name'] = translate_bird_name(original_name)
        detection['original_name'] = original_name

    return recording.detections

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_audio.py <audio_file> [lat] [lon]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    lat = float(sys.argv[2]) if len(sys.argv) > 2 else None
    lon = float(sys.argv[3]) if len(sys.argv) > 3 else None
    
    detections = analyze_audio(file_path, lat, lon)
    
    print(f"Detections in {file_path}:")
    if not detections:
        print("No birds detected.")
    
    for detection in detections:
        print(f" - {detection['common_name']} ({detection['scientific_name']}) "
              f"- Confidence: {detection['confidence']:.2f} "
              f"- Time: {detection['start_time']}s to {detection['end_time']}s")

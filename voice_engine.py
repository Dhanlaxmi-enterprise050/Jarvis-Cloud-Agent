import asyncio
import edge_tts
import os
import base64

async def speak(text: str, output_file: str = "temp_audio_response.mp3", voice: str = 'en-US-JennyNeural') -> str:
    """
    Generates and saves the Text-to-Speech audio to a file.
    Returns the path to the saved file.
    """
    print(f"Generating TTS for: {text[:40]}...")
    try:
        # Generate TTS audio
        tts = edge_tts.Communicate(text, voice)
        
        # Clean up the file if it exists to ensure a fresh save
        if os.path.exists(output_file):
            os.remove(output_file)
            
        await tts.save(output_file)
        return output_file
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""
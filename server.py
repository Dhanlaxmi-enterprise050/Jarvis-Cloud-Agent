import uvicorn
import base64
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the core logic and voice engine
from jarvis_core import execute_browser_task
from voice_engine import speak

# --- INITIALIZATION ---
load_dotenv() # Load environment variables from .env
app = FastAPI(title="Jarvis Cloud Agent API")

# Configure CORS (Allows mobile app to connect from any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Request Model ---
class CommandRequest(BaseModel):
    command: str

# --- API ENDPOINT ---
@app.post("/api/v1/command")
async def process_command(request: CommandRequest):
    
    # 1. Execute the core agent task (Browser Automation)
    agent_result = await execute_browser_task(request.command)
    
    text_response = agent_result.get("final_response")
    visual_proof_b64 = agent_result.get("screenshot_base64", "")
    
    # 2. Generate Text-to-Speech (TTS)
    audio_file_path = "temp_audio_response.mp3"
    await speak(text_response, output_file=audio_file_path)
    
    audio_response_b64 = ""
    
    # 3. Convert MP3 to Base64 and Clean Up
    try:
        with open(audio_file_path, "rb") as audio_file:
            # Base64 encode the audio file content
            audio_response_b64 = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Clean up the temporary file immediately
        os.remove(audio_file_path)
    except FileNotFoundError:
        print(f"Error: TTS file not found at {audio_file_path}. Returning without audio.")
        
    # 4. Return the full response package
    return {
        "text_response": text_response,
        "visual_proof": visual_proof_b64,
        "audio_response": audio_response_b64,
        "status": "success" if visual_proof_b64 else "error"
    }

if __name__ == "__main__":
    # Runs the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
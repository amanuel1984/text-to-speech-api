from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import azure.cognitiveservices.speech as speech_sdk
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
AZURE_SPEECH_KEY = os.getenv('SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('SPEECH_REGION')
API_KEY = os.getenv("API_KEY", "your_default_api_key")  # Fixed variable name

# Debug print to verify API key loading (Remove this in production)
print(f"Loaded API Key: {API_KEY}")

# Initialize Azure Speech Config
speech_config = speech_sdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"

# Initialize FastAPI
app = FastAPI()

# Dependency to check API key (Header uses "api-key" as expected)
def get_api_key(api_key: str = Header(..., alias="api-key")):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Define the input data format
class SpeechRequest(BaseModel):
    text: str

@app.post("/synthesize", dependencies=[Depends(get_api_key)])
async def synthesize_speech(request: SpeechRequest):
    """
    API endpoint to convert text to speech.
    """
    try:
        # Generate SSML (Speech Synthesis Markup Language) for enhanced speech control
        response_ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='en-US-BrianMultilingualNeural'>
                <prosody rate="medium" pitch="low">
                    {request.text}
                </prosody>
            </voice>
        </speak>
        """

        # Configure Speech Synthesizer
        synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_ssml_async(response_ssml).get()

        # Check for successful synthesis
        if result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
            return {"message": "Speech synthesis successful"}
        else:
            raise Exception("Speech synthesis failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", dependencies=[Depends(get_api_key)])
async def root():
    return {"message": "Welcome to the Speech Synthesis API. Use /synthesize to convert text to speech."}

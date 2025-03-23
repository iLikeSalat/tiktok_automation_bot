import os
import requests
import time
import sys
sys.path.append('..')
from utils.logger import setup_logger
from utils.helpers import load_json

# Set up logger
logger = setup_logger('voice_generator')

class VoiceGenerator:
    def __init__(self, config_file='config.json'):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.config = load_json(config_file).get('voice_settings', {})
        self.output_dir = "assets/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("VoiceGenerator initialized")
    
    def generate_voiceover(self, text, voice_id=None):
        """Generate AI voiceover from text"""
        try:
            voice_id = voice_id or self.config.get('default_voice', 'default')
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": self.config.get('stability', 0.75) ,
                    "similarity_boost": self.config.get('similarity_boost', 0.75)
                }
            }
            
            logger.info(f"Generating voiceover with voice ID: {voice_id}")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                timestamp = int(time.time())
                audio_file = os.path.join(self.output_dir, f"voiceover_{timestamp}.mp3")
                
                with open(audio_file, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Voiceover saved to {audio_file}")
                return audio_file
            else:
                logger.error(f"Error generating voiceover: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in generate_voiceover: {e}")
            return None
    
    def generate_from_script(self, script):
        """Generate voiceover from script object"""
        try:
            # Combine script sections
            text = f"{script['hook']} {script['body']} {script['cta']}"
            return self.generate_voiceover(text)
        except Exception as e:
            logger.error(f"Error generating voiceover from script: {e}")
            return None
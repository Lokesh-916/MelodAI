from dotenv import load_dotenv
load_dotenv()

import os
from backend.main_service import MainMusicService

service = MainMusicService(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    out_dir="generated_audio"
)

user_text = "Energetic synthwave for my workout"
audio, logs = service.generate_music_pipeline(user_text)

print("Final audio:", audio)
print("Logs:", logs)

# dotenv load added

# normalized line endings

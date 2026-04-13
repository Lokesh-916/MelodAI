import os
import numpy as np
import soundfile as sf
from pathlib import Path
from transformers import pipeline

DEFAULT_PROMPTS = [
    "upbeat happy pop music",
    "sad slow piano melody",
    "energetic electronic dance music",
    "calm peaceful ambient sounds",
    "romantic acoustic guitar",
    "intense dramatic orchestral",
    "groovy funk bass",
    "mysterious dark atmospheric"
]

def save_audio(audio_array, sample_rate, out_path):
    audio = np.asarray(audio_array, dtype=np.float32)
    if audio.ndim == 2:
        if audio.shape[0] < audio.shape[1]:
            audio = audio.T
        if audio.shape[1] > 2:
            audio = audio[:, 0:1]
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(out_path, audio, sample_rate)

def generate_music(prompts, out_dir="outputs", duration=6):
    os.makedirs(out_dir, exist_ok=True)
    audio_gen = pipeline(task="text-to-audio", model="facebook/musicgen-small")
    max_new_tokens = duration * 50
    results = []

    for i, prompt in enumerate(prompts):
        out = audio_gen(prompt, forward_params={"max_new_tokens": max_new_tokens})
        audio = out["audio"][0]
        sr = out["sampling_rate"]
        path = Path(out_dir) / f"{i+1:02d}_{prompt[:20].replace(' ', '_')}.wav"
        save_audio(audio, sr, path)
        results.append(str(path))

    return results

if __name__ == "__main__":
    files = generate_music(DEFAULT_PROMPTS, out_dir="outputs", duration=6)
    for f in files:
        print(f)

# increased token count for longer clips

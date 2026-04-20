import os
import time
import json
import shutil
import numpy as np
import soundfile as sf
from pathlib import Path
from transformers import pipeline

# pydub + ffmpeg
try:
    from pydub import AudioSegment, effects, silence
    _PYDUB_AVAILABLE = True
except Exception:
    _PYDUB_AVAILABLE = False

# config path
PARAM_CONFIG_PATH = Path(__file__).parent / "param_config.json"


def load_param_config(path=PARAM_CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------

def _ensure_ffmpeg_pydub():
    if not _PYDUB_AVAILABLE:
        raise RuntimeError("pydub is not installed. Run `pip install pydub`.")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is missing. Install using `apt-get install -y ffmpeg`.")


def _float_or_int16(audio):
    audio = np.asarray(audio)
    if audio.dtype in (np.float32, np.float64):
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)
    else:
        audio = audio.astype(np.int16)
    return audio


def _safe_write_wav(path, audio_data, sr):
    audio_int16 = _float_or_int16(audio_data)
    sf.write(str(path), audio_int16, sr, subtype="PCM_16")


def _convert_wav_to_mp3(wav_path, mp3_path, fade_ms=1000):
    _ensure_ffmpeg_pydub()

    seg = AudioSegment.from_wav(str(wav_path))
    seg = effects.normalize(seg)

    if fade_ms > 0:
        seg = seg.fade_in(fade_ms).fade_out(fade_ms)

    ns = silence.detect_nonsilent(seg, min_silence_len=200, silence_thresh=-50)
    if ns:
        start = max(0, ns[0][0] - 50)
        end = min(len(seg), ns[-1][1] + 50)
        seg = seg[start:end]

    seg.export(str(mp3_path), format="mp3", bitrate="192k")
    return str(mp3_path)


# -----------------------------------------------------------
# Main Class
# -----------------------------------------------------------

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-small", param_config=None):
        self.model_name = model_name
        self.pipe = pipeline(task="text-to-audio", model=model_name)
        self.config = param_config or load_param_config()

    # map LLM params → model generation params
    def _map_params(self, params):
        energy = str(params.get("energy", 5))
        temp = self.config["energy_to_temp"].get(energy, self.config["default_temperature"])
        cfg = self.config["energy_to_cfg"].get(energy, self.config["default_cfg"])
        return float(temp), float(cfg)

    # generate single audio
    def generate(self, prompt, duration=30, out_dir="outputs", prefix="gen", retries=2):
        Path(out_dir).mkdir(exist_ok=True)
        token_count = max(8, int(duration * 50))
        last_error = None

        for attempt in range(retries + 1):
            try:
                output = self.pipe(prompt, forward_params={"max_new_tokens": token_count})
                audio = output["audio"][0]
                sr = output["sampling_rate"]

                ts = int(time.time())
                wav_path = Path(out_dir) / f"{prefix}_{ts}.wav"
                mp3_path = Path(out_dir) / f"{prefix}_{ts}.mp3"

                # write wav
                _safe_write_wav(wav_path, audio, sr)

                # convert → mp3
                try:
                    final_file = _convert_wav_to_mp3(wav_path, mp3_path)
                except Exception as conv_err:
                    print("MP3 conversion failed:", conv_err)
                    final_file = str(wav_path)

                return {
                    "file": final_file,
                    "prompt": prompt,
                    "duration": duration,
                    "tokens": token_count,
                    "model": self.model_name,
                    "time": ts
                }

            except Exception as e:
                last_error = e
                time.sleep(0.5)

        raise RuntimeError(f"Music generation failed. Last error: {last_error}")

    # multiple prompts
    def generate_with_mapping(self, params, n_variations=1, out_dir="outputs", prefix="mapped"):
        temp, cfg = self._map_params(params)
        prompts = params.get("enhanced_prompts", [params.get("raw_prompt", "")])

        results = []
        for i, prompt in enumerate(prompts[:n_variations]):
            md = self.generate(prompt, duration=params.get("duration", 30),
                               out_dir=out_dir, prefix=f"{prefix}_{i}")
            md["variation_index"] = i
            results.append(md)

        return results

# _float_or_int16 helper added

# _safe_write_wav using soundfile

# pydub availability check

# _convert_wav_to_mp3 with fade and trim

# _ensure_ffmpeg_pydub guard

# MusicGenerator.__init__ with pipeline

# _map_params energy to temp and cfg

# generate() with retry and wav export

# mp3 conversion inside generate()

# generate_with_mapping for multi-prompt

# fix: explicit ffmpeg check with clear error

# fix: clip float audio before int16 conversion

# refactor: load_param_config at module level

# cleanup: removed unused imports

# improved error messages

# variation_index in result dict

# _float_or_int16 helper

# _safe_write_wav

# pydub check

# _convert_wav_to_mp3

# _ensure_ffmpeg_pydub guard

# MusicGenerator init

# _map_params

# generate() with retry

# mp3 conversion

# generate_with_mapping

# fix: explicit ffmpeg check

# fix: clip float audio

# refactor: module level config

# cleanup: unused imports removed

# improved error messages

# variation_index in result

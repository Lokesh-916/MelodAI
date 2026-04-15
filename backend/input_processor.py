# backend/input_processor.py

import os
import json
import re
import time

try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except Exception:
    Groq = None
    _GROQ_AVAILABLE = False

DEFAULTS = {
    "mood": "neutral",
    "energy": 5,
    "style": "ambient",
    "tempo": "medium",
    "tempo_bpm": 100,
    "instruments": [],
    "duration": 30
}

PROMPT_TEMPLATE = """
Extract music-generation parameters from the following text.
Return ONLY pure JSON exactly in this format:

{{
  "mood": "",
  "energy": 1-10,
  "style": "",
  "tempo": "slow/medium/fast",
  "tempo_bpm": 0,
  "instruments": [],
  "duration": 0,
  "context": ""
}}

User Request: "{u}"
"""

SYSTEM_PROMPT = "You are an assistant that must return strictly valid JSON only."

class InputProcessor:
    def __init__(self, groq_api_key: str = None, model: str = "llama-3.1-8b-instant", max_retries: int = 2):
        key = groq_api_key or os.environ.get("GROQ_API_KEY")
        if key and _GROQ_AVAILABLE:
            self.client = Groq(api_key=key)
        else:
            self.client = None
        self.model = model
        self.max_retries = max_retries

    def _call_llm(self, user_text: str):
        if not self.client:
            return None
        prompt = PROMPT_TEMPLATE.format(u=user_text.replace('"', "'"))
        for attempt in range(self.max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                content = resp.choices[0].message.content
                return content
            except Exception as e:
  
                time.sleep(0.3)
                last_err = e

        try:
            print("Groq call failed:", last_err)
        except Exception:
            pass
        return None

    def _parse_json_block(self, txt: str):
        if not txt:
            return None
        m = re.search(r"\{.*\}", txt, flags=re.DOTALL)
        block = m.group(0) if m else txt
        try:
            return json.loads(block)
        except Exception:
            try:
                return json.loads(block.replace("'", '"'))
            except Exception:
                return None

    def _fallback_parse(self, text: str):
        t = text.lower()
        mood_candidates = ["happy", "sad", "energetic", "calm", "romantic", "intense", "mysterious", "groovy", "relaxed", "angry"]
        mood = next((m for m in mood_candidates if m in t), "neutral")

        if any(k in t for k in ["workout", "energetic", "gym", "cardio"]):
            energy, tempo, tempo_bpm = 9, "fast", 140
        elif any(k in t for k in ["meditation", "calm", "sleep", "relax"]):
            energy, tempo, tempo_bpm = 2, "slow", 60
        elif any(k in t for k in ["study", "focus", "concentration"]):
            energy, tempo, tempo_bpm = 4, "medium", 90
        else:
            energy, tempo, tempo_bpm = 5, "medium", 100

        styles = ["pop", "rock", "electronic", "ambient", "classical", "orchestral", "jazz", "funk", "acoustic", "edm", "lo-fi"]
        style = next((s for s in styles if s in t), "ambient" if mood in ["calm", "neutral"] else "pop")

        instruments_pool = ["piano", "guitar", "violin", "drums", "bass", "synth", "flute", "strings", "vocals", "brass"]
        instruments = [ins for ins in instruments_pool if ins in t]

        duration = DEFAULTS["duration"]
        m = re.search(r"(\d+)\s*(s|sec|seconds|min|m)\b", t)
        if m:
            val = int(m.group(1))
            duration = val * 60 if m.group(2).startswith("m") else val

        for neg in re.findall(r"no\s+([a-z]+)", t):
            instruments = [i for i in instruments if i != neg]

        return {
            "mood": mood,
            "energy": energy,
            "style": style,
            "tempo": tempo,
            "tempo_bpm": tempo_bpm,
            "instruments": instruments,
            "duration": duration,
            "context": text
        }

    def process(self, text: str, use_llm: bool = True):
        if use_llm and self.client:
            raw = self._call_llm(text)
            parsed = self._parse_json_block(raw)
            if parsed and isinstance(parsed, dict):
       
                out = {}
                out["mood"] = parsed.get("mood") or DEFAULTS["mood"]
                try:
                    out["energy"] = int(parsed.get("energy", DEFAULTS["energy"]))
                except Exception:
                    out["energy"] = DEFAULTS["energy"]
                out["style"] = parsed.get("style") or DEFAULTS["style"]
                out["tempo"] = parsed.get("tempo") or DEFAULTS["tempo"]
                out["tempo_bpm"] = parsed.get("tempo_bpm") or DEFAULTS["tempo_bpm"]
                out["instruments"] = parsed.get("instruments") or []
                out["duration"] = parsed.get("duration") or DEFAULTS["duration"]
                out["context"] = parsed.get("context") or text
                return out
            # fallback if parsing failed
        return self._fallback_parse(text)


if __name__ == "__main__":

    sample_prompts = [
        "I want something that starts calm but becomes energetic halfway, maybe with soft piano turning into fast synthwave.",
        "Music for late-night studying but I don’t want sleepy vibes, something focused yet slightly uplifting.",
        "Give me a slow but intense cinematic soundtrack with booming drums, around 40 seconds.",
        "A hopeful emotional song for a long drive, medium pace, preferably with guitars.",
        "Desert vibes with deep bass and echoing vocals.",
        "No drums please, just smooth lo-fi vibes for 25 seconds, something warm and soft.",
        "Aggressive jazz track, but keep the overall feeling calm.",
        "A melody led by flute with soft pads behind it, slow tempo, meditative mood.",
        "140 BPM workout track but keep the tone uplifting instead of hardcore.",
        "Make it feel like walking through a neon city in the rain — shimmering textures, medium tempo."
    ]

    key = os.environ.get("GROQ_API_KEY")
    proc = InputProcessor(groq_api_key=key)
    print("Running test harness for InputProcessor. Using LLM:", bool(proc.client))
    outputs = []
    for i, p in enumerate(sample_prompts, 1):
        res = proc.process(p, use_llm=True)
        outputs.append(res)
        print(f"\nTest {i} Input: {p}")
        print("Output:")
        print(json.dumps(res, indent=2))


    try:
        out_path = "input_processor_test_outputs.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2)
        print(f"\nSaved test outputs to {out_path}")
    except Exception:
        pass

# TODO: add groq client init

# groq client wired up

# _call_llm implemented with retry

# _parse_json_block added

# fallback parser added

# duration parsing from sec and min

# negative instrument exclusion handled

# process() method complete

# __main__ test harness added

# single-quote fallback for json parsing

# test outputs saved to json

# fix: strip markdown code fences from groq response

# context field added to fallback output

# strip whitespace from llm response

# DEFAULTS and PROMPT_TEMPLATE added

# groq client wired up

# _call_llm with retry

# _parse_json_block with regex

# _fallback_parse keyword matching

# duration parsing

# negative instrument exclusion

# process() complete

# __main__ test harness

# single-quote json fallback

# test outputs saved

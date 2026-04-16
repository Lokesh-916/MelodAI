import json
import random
from pathlib import Path

MOOD_TEMPLATES_PATH = Path(__file__).parent / "mood_templates.json"

def load_mood_templates(path=MOOD_TEMPLATES_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class PromptEnhancer:
    def __init__(self, mood_templates=None):
        self.templates = mood_templates or load_mood_templates()

    def build_core(self, params):
        mood = params.get("mood", "neutral")
        style = params.get("style", "")
        tempo = params.get("tempo_bpm", params.get("tempo", "medium"))
        instruments = params.get("instruments", [])
        duration = params.get("duration", None)
        context = params.get("context", "")

        base = self.templates.get(mood, "").format(tempo=tempo)

        parts = [base]
        if style:
            parts.append(f"genre: {style}")
        if instruments:
            parts.append("instruments: " + ", ".join(instruments))
        if duration:
            parts.append(f"duration: ~{duration}s")
        if context:
            parts.append(f"context: {context}")

        return ". ".join(parts)

    def add_terms(self, core, params):
        energy = params.get("energy", 5)
        if energy >= 8:
            addon = "strong accents, fast rhythmic movement"
        elif energy >= 5:
            addon = "steady groove, balanced rhythm"
        else:
            addon = "soft textures, gentle layers"
        return f"{core}. {addon}. structure: intro - build - motif - outro"

    def enhance(self, params, n_variations=3):
        core = self.build_core(params)
        enriched = self.add_terms(core, params)

        variations = []
        for _ in range(n_variations):
            v = enriched
            if params.get("instruments"):
                inst = params["instruments"][:]
                random.shuffle(inst)
                v = v.replace(", ".join(params["instruments"]), ", ".join(inst))

            if random.random() < 0.3:
                extra = random.choice([
                    "wide stereo field",
                    "clean production",
                    "layered harmonics",
                    "ambient spatial depth"
                ])
                v = f"{v}. production: {extra}"

            variations.append({"prompt": v, "valid": True, "reason": "ok"})
        return variations

# build_core implemented

# add_terms implemented

# enhance() with n_variations

# random instrument shuffle in variations

# production note injection at 30pct

# refactor: mood template loading at module level

# build_core implemented

# add_terms implemented

# enhance() with n_variations

# random instrument shuffle

# production note injection

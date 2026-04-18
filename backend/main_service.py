import os
import json
from pathlib import Path

from backend.input_processor import InputProcessor
from backend.prompt_enhancer import PromptEnhancer
from backend.music_generator import MusicGenerator


class MainMusicService:
    def __init__(self, groq_api_key=None, out_dir="final_outputs", model_name="facebook/musicgen-small"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)

        self.processor = InputProcessor(groq_api_key=groq_api_key)
        self.enhancer = PromptEnhancer()
        self.generator = MusicGenerator(model_name=model_name)

    def generate_music_pipeline(self, user_input):
        logs = {}

        try:
            params = self.processor.process(user_input, use_llm=True)
            logs["params"] = params
        except Exception as e:
            logs["processing_error"] = str(e)
            return None, logs

        try:
            enhanced = self.enhancer.enhance(params, n_variations=3)
            valid = [x["prompt"] for x in enhanced if x["valid"]]
            final_prompt = valid[0] if valid else user_input
            params["enhanced_prompts"] = valid
            logs["chosen_prompt"] = final_prompt
        except Exception as e:
            logs["enhance_error"] = str(e)
            return None, logs

        try:
            params["raw_prompt"] = user_input
            result = self.generator.generate_with_mapping(params, n_variations=1, out_dir=str(self.out_dir), prefix="final")
            logs["generation"] = result
            return result[0]["file"], logs
        except Exception as e:
            logs["generation_error"] = str(e)
            return None, logs


if __name__ == "__main__":
    service = MainMusicService(groq_api_key=os.environ.get("GROQ_API_KEY"))

    tests = [
        "I need energetic music for my workout",
        "Something calm for meditation"]
        # "Romantic dinner guitar melody",
        # "Fast paced EDM for 40 seconds",
        # "Slow piano solo for relaxing",
        # "Happy birthday celebration tune",
        # "Dark mysterious atmospheric track",
        # "Groovy funk bass for dancing",
        # "Sad emotional violin based melody",
        # "Ambient study background"
    

    results = []
    for t in tests:
        audio, log = service.generate_music_pipeline(t)
        print("Input:", t)
        print("Audio:", audio)
        print("Logs:", json.dumps(log, indent=2))
        results.append({"input": t, "audio": audio, "log": log})

    with open("pipeline_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

# InputProcessor wired in

# PromptEnhancer wired in

# MusicGenerator wired in

# generate_music_pipeline orchestration

# structured logs dict added

# error handling per stage

# __main__ test prompts added

# ensure out_dir exists

# removed debug prints

# end to end verified

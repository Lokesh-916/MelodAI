from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile as wav
import torch

# 1. Load Processor & Model
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
print("Script started")


# Move to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# 2. Your Text Prompt
prompts = ["upbeat happy pop music",
"sad slow piano melody",
"energetic electronic dance music",
"calm peaceful ambient sounds",
"romantic acoustic guitar",
"intense dramatic orchestral",
"groovy funk bass",
"mysterious dark atmospheric"]

for i,prompt in enumerate(prompts,1):
    print(f"Generating music for prompt: {prompt}")
# 3. Convert prompt to model input
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt"
    ).to(device)

    # 4. Generate audio (5–10 sec)
    audio_values = model.generate(
        **inputs,
        max_new_tokens=512  # increase to 512 for ~10s
    )

    # 5. Convert to numpy
    audio_array = audio_values[0, 0].cpu().numpy()

    # 6. Save as WAV
    sample_rate = 32000  # standard for MusicGen
    wav.write(f"output_{i}.wav", sample_rate, audio_array)

    print(f"Saved as output_{i}.wav")

# verified output shape and sample rate

# tested multiple prompts in loop

# fixed audio array shape

# verified output shape and sample rate

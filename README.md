<div align="center">

<h1>
  <img src="https://img.shields.io/badge/MelodAI-Music%20Generation-8A2BE2?style=for-the-badge&logoColor=white" alt="MelodAI"/>
</h1>

<p><em>Turn a sentence into a song.</em></p>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co/facebook/musicgen-small)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-F54E00?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## What is MelodAI?

MelodAI is an end-to-end AI pipeline that converts plain English descriptions into original music. You type something like *"a calm lo-fi track for late night studying"* and the system figures out the mood, tempo, instruments, and energy level — then generates a real audio file from scratch.

No music theory knowledge required. No DAW. Just words.

---

## How It Works

The pipeline has three distinct stages, each handled by a dedicated module:

```
User Prompt
    │
    ▼
┌─────────────────────┐
│   Input Processor   │  ← Groq LLM (LLaMA 3.1) extracts structured params
│  input_processor.py │    Falls back to regex/keyword parsing if LLM fails
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Prompt Enhancer   │  ← Builds a rich music generation prompt
│  prompt_enhancer.py │    Uses mood templates + energy descriptors
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Music Generator   │  ← Facebook MusicGen via HuggingFace Transformers
│  music_generator.py │    Outputs .wav / .mp3 with post-processing
└─────────────────────┘
```

---

## Pipeline Stages

### Stage 1 — Input Processing

The `InputProcessor` takes a raw text prompt and extracts structured music parameters. It first tries the Groq API (LLaMA 3.1-8b) for accurate semantic understanding. If the API is unavailable or returns malformed JSON, it falls back to a keyword/regex parser.

**Output parameters:**

| Parameter | Type | Example |
|-----------|------|---------|
| `mood` | string | `"calm"`, `"energetic"`, `"mysterious"` |
| `energy` | int (1–10) | `7` |
| `style` | string | `"synthwave"`, `"ambient"`, `"jazz"` |
| `tempo` | string | `"slow"`, `"medium"`, `"fast"` |
| `tempo_bpm` | int | `128` |
| `instruments` | list | `["piano", "synth", "drums"]` |
| `duration` | int (seconds) | `30` |

---

### Stage 2 — Prompt Enhancement

The `PromptEnhancer` takes the structured parameters and builds a detailed, model-optimized prompt. It uses a set of mood templates and energy-based descriptors to produce up to 3 prompt variations, adding production notes and structural cues like *intro → build → motif → outro*.

**Mood template example:**

```json
"calm": "soft pads, slow movement, ambient textures, gentle mood, {tempo} BPM"
```

---

### Stage 3 — Music Generation

The `MusicGenerator` feeds the enhanced prompt into [facebook/musicgen-small](https://huggingface.co/facebook/musicgen-small) via the HuggingFace `transformers` pipeline. The energy level is mapped to model temperature and CFG scale for fine-grained control over output character.

**Energy → Model Parameter Mapping:**

| Energy Level | Temperature | CFG Scale | Character |
|:---:|:---:|:---:|---|
| 1–2 | 0.4–0.5 | 1.0–1.2 | Very soft, minimal |
| 3–4 | 0.7–0.8 | 1.5–2.0 | Gentle, restrained |
| 5–6 | 1.0–1.1 | 3.0–3.5 | Balanced, natural |
| 7–8 | 1.2–1.4 | 4.0–4.5 | Driven, expressive |
| 9–10 | 1.6–1.8 | 5.0–6.0 | Intense, high-energy |

Post-processing includes normalization, fade in/out, and silence trimming via `pydub`.

---

## Project Structure

```
MelodAI/
├── backend/
│   ├── input_processor.py     # LLM + fallback param extraction
│   ├── prompt_enhancer.py     # Prompt construction and variation
│   ├── music_generator.py     # MusicGen inference + audio export
│   ├── main_service.py        # Orchestrates the full pipeline
│   ├── mood_templates.json    # Per-mood base prompt templates
│   └── param_config.json      # Energy → temperature/CFG mappings
├── samples/                   # Sample generated audio files
├── run_pipeline.py            # Entry point script
├── hf_approach.py             # Early HuggingFace experiment
├── test_musicgen.py           # Standalone generation test harness
├── requirements.txt
└── .env                       # GROQ_API_KEY (not committed)
```

---

## Getting Started

**1. Clone and set up environment**

```bash
git clone https://github.com/Lokesh-916/MelodAI.git
cd MelodAI
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Add your Groq API key**

```bash
# Create a .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

Get a free key at [console.groq.com](https://console.groq.com).

**3. Run the pipeline**

```bash
python run_pipeline.py
```

Or use it programmatically:

```python
from backend.main_service import MainMusicService

service = MainMusicService(groq_api_key="your_key")
audio_file, logs = service.generate_music_pipeline("Calm piano for late night studying")
print(audio_file)  # path to generated .wav or .mp3
```

---

## Sample Prompts

| Prompt | Mood | Energy | Style |
|--------|------|--------|-------|
| `"Energetic synthwave for my workout"` | energetic | 9 | synthwave |
| `"Calm meditation background, no drums"` | calm | 2 | ambient |
| `"Dark cinematic score with booming drums"` | intense | 8 | orchestral |
| `"Groovy late night jazz, medium tempo"` | groovy | 5 | jazz |
| `"Soft lo-fi for studying, 25 seconds"` | calm | 3 | lo-fi |

---

## Requirements

```
transformers
torchaudio
accelerate
pydub
soundfile
scipy
groq
python-dotenv
openai
streamlit
```

> ffmpeg must be installed separately for MP3 export. On Ubuntu: `apt-get install -y ffmpeg`. On Windows: download from [ffmpeg.org](https://ffmpeg.org).

---

## Limitations

- Generation time depends on hardware. CPU inference is slow (~1–3 min per clip). GPU recommended.
- `musicgen-small` produces clips up to ~30 seconds reliably. Longer durations may degrade quality.
- The LLM fallback parser handles common cases but may miss nuanced prompts.

---

<div align="center">

Built with [Facebook MusicGen](https://github.com/facebookresearch/audiocraft) · [Groq](https://groq.com) · [HuggingFace Transformers](https://huggingface.co/docs/transformers)

</div>

<!-- pipeline diagram section -->

<!-- energy mapping table -->

<!-- sample prompts and usage -->

<!-- limitations section added -->

<!-- pipeline diagram -->

<!-- energy table -->

<!-- sample prompts -->

<!-- limitations -->

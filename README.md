# AI-Assisted Binary Deobfuscator

An automated reverse-engineering pipeline that leverages Headless Ghidra and Large Language Models (LLMs) to analyze, deobfuscate, and document stripped executable binaries. 

This tool extracts decompiled C-code, analyzes standard and obfuscated logic using the Google Gemini API, and automatically reintegrates descriptive function names, variable names, and purpose comments directly back into the Ghidra database.

## Features
* **Headless Ghidra Automation:** Extracts assembly and pseudo-C code without opening the GUI.
* **Smart Filtering:** Bypasses standard C-library boilerplate (e.g., `_init`, `__libc_start_main`) to conserve API quota and execution time.
* **LLM Semantic Analysis:** Uses Gemini (or other configured LLMs) to deduce the underlying purpose of generically named functions (e.g., `FUN_001050` -> `validate_key_or_print_usage`).
* **Automated Database Reintegration:** Injects AI-generated intelligence directly into the Ghidra Symbol Tree and Decompiler views via automated Java scripting.

## Architecture
The pipeline operates through four modular subsystems:
1. **The CLI & Config (`main.py`, `config.yaml`):** Handles user input and secures API credentials.
2. **The Core Orchestrator (`orchestrator.py`):** Manages the three-pass execution lifecycle, handles API rate-limits, and coordinates data flow between Ghidra and the AI.
3. **The API Brain (`prompt_templates.py`, `llm_client.py`):** Enforces strict JSON schemas on the LLM to ensure parsed outputs map perfectly back to local variables and functions.
4. **The JVM Scripts (`ExtractFunctions.java`, `ApplyLabels.java`):** Runs natively inside Ghidra to safely extract data and commit new labels/comments using Ghidra's Transaction API.

## Prerequisites
* Ghidra (configured at `/usr/share/ghidra`)
* Python 3.x
* A Google AI Studio API Key (Free tier supported via rate-limit handling)

## Usage

1. **Configure API Key:**
   Update `utils/config.yaml` with your Gemini API key.

2. **Prepare the Target:**
   Place your compiled binary (e.g., a malware sample or crackme) into the `data/malware_samples/` directory.

3. **Run the Pipeline:**
   ```bash
   python3 main.py data/malware_samples/crackme

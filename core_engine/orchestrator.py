# core_engine/orchestrator.py
import subprocess
import json
import os
import shutil
import time
from core_engine.llm_client import ask_gemini
from core_engine.prompt_templates import SYSTEM_PROMPT, format_user_prompt

GHIDRA_HEADLESS = "/usr/share/ghidra/support/analyzeHeadless"
EXTRACTED_JSON = "extracted_functions.json"
OUTPUT_JSON = "ai_annotations.json"
PROJECT_DIR = "/tmp/ghidra_proj"
PROJECT_NAME = "DeobfuscatorProject"

def setup_project_dir():
    if os.path.exists(PROJECT_DIR):
        shutil.rmtree(PROJECT_DIR)
    os.makedirs(PROJECT_DIR, exist_ok=True)

def run_ghidra_extraction(binary_path):
    print(f"[*] [Pass 1] Importing binary & extracting code: {binary_path}")
    setup_project_dir()
    
    command = [
        GHIDRA_HEADLESS,
        PROJECT_DIR, PROJECT_NAME,
        "-import", binary_path,
        "-scriptPath", "ghidra_scripts",
        "-postScript", "ExtractFunctions.java"
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Ghidra extraction complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Ghidra extraction failed: {e}")
        return False

def process_with_ai():
    print("[*] [Pass 2] Analyzing decompiled functions with Gemini...")
    if not os.path.exists(EXTRACTED_JSON):
        print("[-] Extraction file not found.")
        return False

    with open(EXTRACTED_JSON, "r") as f:
        functions = json.load(f)

    ai_results = {}
    ignored_prefixes = ('_', 'register_tm_clones', 'deregister_tm_clones', 'frame_dummy', 'puts')

    for func_name, c_code in functions.items():
        if func_name.startswith(ignored_prefixes):
            continue

        print(f"    -> Analyzing: {func_name}...")
        user_prompt = format_user_prompt(func_name, c_code)
        result = ask_gemini(SYSTEM_PROMPT, user_prompt)
        
        if result:
            ai_results[func_name] = result
        
        time.sleep(15)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(ai_results, f, indent=4)
        
    print(f"[+] AI analysis saved to {OUTPUT_JSON}")
    return True

def run_ghidra_reintegration(binary_path):
    binary_filename = os.path.basename(binary_path)
    print(f"[*] [Pass 3] Reintegrating annotations into Ghidra database for: {binary_filename}")

    command = [
        GHIDRA_HEADLESS,
        PROJECT_DIR, PROJECT_NAME,
        "-process", binary_filename,
        "-noanalysis",
        "-scriptPath", "ghidra_scripts",
        "-postScript", "ApplyLabels.java"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # Display the custom script logs from Ghidra output
        for line in result.stdout.splitlines():
            if "[+]" in line or "[*]" in line or "Renamed" in line:
                print(f"    {line}")
        print("[+] Reintegration complete. Ghidra project updated.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Reintegration failed: {e}")
        return False

def run_pipeline(binary_path):
    if not os.path.exists(binary_path):
        print(f"[-] Binary not found: {binary_path}")
        return

    if run_ghidra_extraction(binary_path):
        if process_with_ai():
            run_ghidra_reintegration(binary_path)

# core/llm_client.py
import requests
import yaml
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def ask_gemini(system_prompt, user_prompt):
    config = load_config()
    api_key = config['llm']['api_key']
    model = config['llm']['model']
    temperature = config['llm']['temperature']

    if api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("[-] Error: Please set your API key in utils/config.yaml")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Structure the payload for Gemini API
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt + "\n\n" + user_prompt}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json" # Force JSON output
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse the Gemini response structure
        result_json = response.json()
        llm_text = result_json['candidates'][0]['content']['parts'][0]['text']
        
        # Convert the returned text string back into a Python dictionary
        return json.loads(llm_text)
        
    except requests.exceptions.RequestException as e:
        print(f"[-] API Request failed: {e}")
        if response.text:
            print(f"[-] API Response: {response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"[-] Failed to parse LLM output as JSON: {e}")
        print(f"Raw output: {llm_text}")
        return None

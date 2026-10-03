# main.py
import argparse
from core_engine.orchestrator import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="AI-Assisted Binary Deobfuscator")
    parser.add_argument(
        "binary", 
        help="Path to the executable file you want to analyze (e.g., data/benign_samples/test_bin)"
    )
    
    args = parser.parse_args()
    
    print(r"""
         ___  ____       ____             __      ___             __        
        / _ |/  _/      / __ \___  ___   / /  ___/ /__ _____ ___ / /____  _ 
       / __ |/ /       / /_/ / -_)/ _ \ / _ \/ _  / _ `/ __// _ `/ __/  ' \ 
      /_/ |_/___/     /_____/\__/ \___//_.__/\_,_/\_,_/_/   \_,_/\__/_/_/_/ 
    """)
    
    run_pipeline(args.binary)

if __name__ == "__main__":
    main()


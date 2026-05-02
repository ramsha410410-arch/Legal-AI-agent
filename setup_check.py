#!/usr/bin/env python3
# ============================================================
# setup_check.py — Pre-flight Checks Before Running the App
# ============================================================
#
# Run this script FIRST to verify everything is set up correctly:
#   python setup_check.py
#
# It checks:
# - Python version
# - Required packages installed
# - .env file exists
# - Ollama is running
# - Ollama models are downloaded
# ============================================================

import sys
import os
import subprocess

def print_header():
    print("\n" + "="*60)
    print("  ⚖️  Legal AI Agent — Setup Checker")
    print("="*60 + "\n")

def check_python_version():
    print("📌 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} — OK")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} — Need Python 3.10+")
        print("     Download from: https://python.org")
        return False

def check_packages():
    print("\n📌 Checking required packages...")
    
    required = [
        ("streamlit", "streamlit"),
        ("langgraph", "langgraph"),
        ("langchain", "langchain"),
        ("langchain_ollama", "langchain-ollama"),
        ("dotenv", "python-dotenv"),
        ("PyPDF2", "PyPDF2"),
        ("docx", "python-docx"),
        ("pydantic", "pydantic"),
    ]
    
    all_ok = True
    for import_name, pip_name in required:
        try:
            __import__(import_name)
            print(f"  ✅ {pip_name}")
        except ImportError:
            print(f"  ❌ {pip_name} — Run: pip install {pip_name}")
            all_ok = False
    
    return all_ok

def check_env_file():
    print("\n📌 Checking .env file...")
    
    if os.path.exists(".env"):
        print("  ✅ .env file found")
        
        # Check for important variables
        from dotenv import load_dotenv
        load_dotenv()
        
        checks = [
            ("OLLAMA_MODEL", "ollama model name"),
            ("DEFAULT_LLM_PROVIDER", "LLM provider"),
        ]
        
        for var, desc in checks:
            value = os.getenv(var)
            if value:
                print(f"  ✅ {var} = {value}")
            else:
                print(f"  ⚠️  {var} not set (using default)")
        
        return True
    else:
        print("  ❌ .env file NOT found!")
        print("     Run: cp .env.example .env")
        print("     Then edit .env with your settings")
        return False

def check_ollama():
    print("\n📌 Checking Ollama...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        
        if response.status_code == 200:
            print("  ✅ Ollama is running")
            
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"  ✅ Models available:")
                for model in models:
                    print(f"     - {model['name']}")
            else:
                print("  ⚠️  No models downloaded!")
                print("     Run: ollama pull llama3")
            
            return True
        else:
            print("  ❌ Ollama returned error")
            return False
            
    except Exception:
        print("  ❌ Ollama is NOT running")
        print("     1. Download from: https://ollama.ai")
        print("     2. Run: ollama serve")
        print("     3. In a new terminal: ollama pull llama3")
        return False

def check_data_directories():
    print("\n📌 Checking data directories...")
    
    dirs = [
        "./data/legal_knowledge",
        "./data/chroma_db",
    ]
    
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✅ {d}")
        else:
            os.makedirs(d, exist_ok=True)
            print(f"  📁 Created: {d}")
    
    return True

def main():
    print_header()
    
    results = []
    results.append(("Python Version", check_python_version()))
    results.append(("Packages", check_packages()))
    results.append(("Environment File", check_env_file()))
    results.append(("Ollama", check_ollama()))
    results.append(("Data Directories", check_data_directories()))
    
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🚀 Everything looks good!")
        print("   Run the app with: streamlit run app.py")
        print("   Open: http://localhost:8501\n")
    else:
        print("\n⚠️  Fix the issues above before running the app.")
        print("   See README.md for detailed setup instructions.\n")

if __name__ == "__main__":
    main()

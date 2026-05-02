#!/usr/bin/env python
"""
Simple script to start Streamlit with proper error handling
"""
import subprocess
import sys
import time

print("=" * 60)
print("Starting Streamlit Legal AI Agent")
print("=" * 60)

# Run streamlit
try:
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=r"C:\Users\DELL\Downloads\legal_ai_agent_complete\legal_ai_agent"
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Clean setup script for legal_ai_agent
Write-Host "Starting setup..." -ForegroundColor Green

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Copy .env file
Write-Host "Creating .env file..." -ForegroundColor Cyan
if (Test-Path ".env.example") {
    Copy-Item -Path ".env.example" -Destination ".env" -Force
    Write-Host ".env file created successfully" -ForegroundColor Green
}

# Install from requirements.txt
Write-Host "Installing packages from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet

Write-Host "Setup complete! Run 'streamlit run app.py' to start." -ForegroundColor Green
Write-Host "In another terminal, run 'ollama serve'" -ForegroundColor Yellow

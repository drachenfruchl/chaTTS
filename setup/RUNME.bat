@echo off

python --version >nul 2>&1 || (
  echo Python is not installed!
  pause
  exit /b
)

python -m pip install -r requirements.txt

cls 
echo Finished downloading requirements (edge-tts, better-profanity, pyinstaller)
echo You can close this window and delete the file
echo:

pause
exit /b
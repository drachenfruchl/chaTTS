@echo off

pyinstaller ./exe_wrapper.py --noconsole --onefile --clean --name Titanfall2 --icon ./icon.ico
cls

echo Wrapper created (dist/Titanfall2.exe) 
echo:
echo !! Create a backup of the original 'Titanfall2.exe' and store it somewhere !!
echo !! Rename the original 'Titanfall2.exe' into 'Titanfall2_real.exe' !!
echo:
echo Move the newly created pink wrapper .exe into your 'Titanfall2' directory 
echo:

pause
exit /b
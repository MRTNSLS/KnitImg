@echo off
REM Build script for Windows

echo Installing PyInstaller...
pip install pyinstaller

echo Building standalone executable...
FOR /F "tokens=*" %%g IN ('python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"') do (SET CTK_PATH=%%g)

pyinstaller --noconfirm --onedir --windowed --name "KnitImg" --hidden-import "PIL._tkinter_finder" --add-data "%CTK_PATH%;customtkinter/" "main.py"

echo Build complete! Look in the 'dist\KnitImg' folder for your executable.
pause

#!/bin/bash
# Build script for Linux and macOS

echo "Installing PyInstaller..."
pip install pyinstaller

echo "Building standalone executable..."
# Find customtkinter path to include its assets
CTK_PATH=$(python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))")

# macOS and Linux use different path separators for --add-data
if [[ "$OSTYPE" == "darwin"* ]]; then
    SEPARATOR=":"
else
    SEPARATOR=":"
fi

pyinstaller --noconfirm --onedir --windowed --name "KnitImg" --hidden-import "PIL._tkinter_finder" --add-data "${CTK_PATH}${SEPARATOR}customtkinter/" "main.py"

echo "Build complete! Look in the 'dist/KnitImg' folder for your executable."

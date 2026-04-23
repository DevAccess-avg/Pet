# Build script for Windows desktop pet
# Run from the MousePet root folder in PowerShell.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
python create_assets.py

pyinstaller --noconfirm --windowed --onefile --icon assets/app_icon.ico --add-data "assets;assets" main.py

Write-Output "Build complete. The executable is in the dist folder."
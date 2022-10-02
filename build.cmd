pip install -r requirements.txt
pyinstaller --onefile main.py
cd dist
del outrunpy.exe
rename main.exe outrunpy.exe
cd ..
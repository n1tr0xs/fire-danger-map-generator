Приложение было разработано в рамках автоматизации процессов УГМС по ЛНР.
Приложение создает карту пожароопасноти ЛНР.

---
Сборка исходного когда (необходимы `Python >=3.11`, `pyinstaller`):
```
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --log-level FATAL --onedir --name "Fire danger map generator" --contents-directory "." --noconsole --icon "icon.ico" --add-data "icon.ico";"." --add-data "region_coords.txt";"." --add-data "station_regions.txt";"." --add-data "times.ttf";"." --add-data "blank.png";"." "main.py"
```

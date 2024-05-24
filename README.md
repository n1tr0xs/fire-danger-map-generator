Приложение было разработано в рамках автоматизации процессов УГМС по ЛНР.  
Оно создает карту пожароопасноти.

---
Для разработчиков:
1. `blank.png` - шаблон файлы карты (рекомендуется создавать в специализированных графических приложениях (`Photoshop`), так как правило покраски `Pillow` не рабоают с картами, отрисованными в `mspaint` `Paint 3D`).
2. `icon.ico`, `icon.png` - иконки приложения.
3. `region_coords.txt` - координаты размещаемых меток и точек покраски областей.
4. `station_regions.txt` - словарь станция-регионы.

---
Сборка исходного когда (необходимы `Python >=3.11`, `pyinstaller`):
```
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --log-level FATAL --onedir --name "Fire danger map generator" --contents-directory "." --noconsole --icon "icon.ico" --add-data "icon.ico";"." --add-data "region_coords.txt";"." --add-data "station_regions.txt";"." --add-data "times.ttf";"." --add-data "blank.png";"." "main.py"
```

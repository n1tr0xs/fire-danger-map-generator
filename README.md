# О программе
Программа генерирует карту пожароопасноти.
Программа была разработана в рамках автоматизации процессов УГМС по ЛНР.

# Для разработчиков:
1. [blank.png](blank.png) - шаблон файлы карты (рекомендуется создавать в специализированных графических приложениях (`Photoshop`), так как правило покраски `Pillow` не рабоают с картами, отрисованными в `mspaint` `Paint 3D`).
2. [icon.ico](icon.ico), [icon.png](icon.png) - иконки приложения.
3. [region_coords.txt](region_coords.txt) - координаты размещаемых меток и точек покраски областей.
4. [station_regions.txt](station_regions.txt) - словарь станция-регионы.
---
Сборка исходного когда (необходимы `Python >=3.11`, `pyinstaller`):
```Batchfile
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --log-level FATAL --onedir --name "Fire danger map generator" --contents-directory "." --noconsole --icon "icon.ico" --add-data "icon.ico";"." --add-data "region_coords.txt";"." --add-data "station_regions.txt";"." --add-data "times.ttf";"." --add-data "blank.png";"." "main.py"
```

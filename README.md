Это приложение красит шаблон карты, а также размещает на нем числовые метки соответственно с введеными данными в интерфейсе.
Приложение было разработано в рамках автоматизации процессов УГМС по ЛНР.

---
Сборка исходного когда с использованием `pyinstaller`:
```
pip install -r requirements.txt
pyinstaller --noconfirm --clean --log-level FATAL --onedir --name "Fire danger map generator" --contents-directory "." --noconsole --icon "icon.ico" --add-data "icon.ico";"." --add-data "region_coords.txt";"." --add-data "station_regions.txt";"." --add-data "times.ttf";"." --add-data "blank.png";"." "main.py"
```

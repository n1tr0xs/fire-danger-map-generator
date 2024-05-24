Это приложение красит шаблон карты, а также размещает на нем числовые метки соответственно с введеными данными в интерфейсе.
Приложение было разработано в рамках автоматизации процессов УГМС по ЛНР.

---
Сборка исходного когда (необходимы `Python >=3.11`, `pyinstaller`):
1. Обновление pip
```
python -m pip install --upgrade pip

```
2. Установка зависимостей
```
pip install -r requirements.txt
pip install pyinstaller

```
3. Сборка приложения
```
pyinstaller --noconfirm --clean --log-level FATAL --onedir --name "Fire danger map generator" --contents-directory "." --noconsole --icon "icon.ico" --add-data "icon.ico";"." --add-data "region_coords.txt";"." --add-data "station_regions.txt";"." --add-data "times.ttf";"." --add-data "blank.png";"." "main.py"

```

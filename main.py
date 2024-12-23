import sys
import subprocess
import datetime
import traceback
import json

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool, QObject, QRunnable, pyqtSignal
from PyQt6.QtWidgets import *

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt

ICON_PATH = 'icon.ico'
BLANK_PATH = 'blank.png'
FONT_PATH = 'times.ttf'
IMAGE_NAME_TEMPLATE = "Карта пожарной опасности {day:02}.{month:02}.{year:04}.png"

try:
    open(BLANK_PATH)
except FileNotFoundError:
    with open('log.txt', 'a') as log:
        log.write(f'{BLANK_PATH} not found')
    exit(1)

try:
    with open('station_regions.txt', 'r', encoding='utf-8') as fin:
        station_regions = json.loads(fin.read())
except FileNotFoundError:
    print('station_regions.txt not found')
try:
    with open('region_coords.txt', 'r', encoding='utf-8') as fin:
        region_coords = json.loads(fin.read())
except FileNotFoundError:
    print('station_regions.txt not found')


def value_to_color(value):
    '''
    Converts fire danger value to color.
    '''
    if value > 10000:
        return (255, 0, 0)
    if value > 4000:
        return (192, 0, 0)
    if value > 1000:
        return (255, 255, 0)
    if value > 300:
        return (0, 112, 192)
    return (146, 208, 80)


def value_to_class(value):
    '''
    Converts fire danger value to fire danger class.
    '''
    if value > 10000:
        return 'V'
    if value > 4000:
        return 'IV'
    if value > 1000:
        return 'III'
    if value > 300:
        return 'II'
    return 'I'


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing
    progress
        ImageQt to draw
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal()
    progress = pyqtSignal(ImageQt)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit()  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class HLine(QFrame):
    def __init__(self):
        '''
        Creates horizontal line shaped QFrame
        '''
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)


class IntLineEdit(QLineEdit):
    validator = QtGui.QIntValidator()

    def __init__(self):
        '''
        Creates QLineEdit with QIntValidator.
        '''
        super().__init__()
        self.setValidator(self.validator)

    def getInt(self, default: int = 0):
        '''
        Returns integer value of input text or `default` value if it's can't be converted.
        '''
        try:
            return int(self.text())
        except ValueError:
            return default


class MainWindow(QMainWindow):
    def __init__(self):
        '''
        Creates main window.
        '''
        super().__init__()

        self.settings = QtCore.QSettings('n1tr0xs', 'fire danger map generator')
        self.threadpool = QThreadPool.globalInstance()
        self.image_name = ''

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(20)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

        self.setFont(QtGui.QFont('Times New Roman', 16))

        self.setWindowTitle('Генератор карты пожароопасности')
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        label = QLabel('Станция')
        self.layout.addWidget(label, 0, 0)

        label = QLabel('Районы')
        self.layout.addWidget(label, 0, 1)

        label = QLabel('Показатель гориморсти')
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(label, 0, 2)

        label = QLabel('Предпросмотр')
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(label, 0, 3, 1, 2)

        line = HLine()
        self.layout.addWidget(line, 1, 0, 1, 5)

        self.station_edit = {}
        i = 0
        for station in station_regions:
            i += 2

            label = QLabel(station)
            self.layout.addWidget(label, i, 0)

            label = QLabel('\n'.join(region for region in station_regions[station]))
            self.layout.addWidget(label, i, 1)

            edit = IntLineEdit()
            self.station_edit[station] = edit
            self.layout.addWidget(edit, i, 2)

            line = HLine()
            self.layout.addWidget(line, i + 1, 0, 1, 3)

        self.buttonSubmit = QPushButton('Сгенерировать картинку')
        self.buttonSubmit.clicked.connect(self.start_draw)
        self.layout.addWidget(self.buttonSubmit, i + 2, 0, 1, 3)

        self.buttonShowImage = QPushButton('Перейти к картинке')
        self.buttonShowImage.setEnabled(False)
        self.buttonShowImage.clicked.connect(
            lambda x: subprocess.Popen(fr'explorer /select,"{self.image_name}"')
        )
        self.layout.addWidget(self.buttonShowImage, i + 3, 0, 1, 3)

        self.restore_settings()
        self.show()

        self.preview_image_height = self.sizeHint().height()
        self.imageLabel = QLabel()
        self.redraw_preview(ImageQt(Image.open(BLANK_PATH)))
        self.layout.addWidget(self.imageLabel, 2, 3, len(station_regions.keys()) * 2 + 2, 2)
        self.setFixedSize(self.sizeHint())

    def start_draw(self):
        '''
        Starts the draw function worker in another Thread.
        Binds signals of worker.
        '''
        self.buttonSubmit.setEnabled(False)
        worker = Worker(self.draw_map)
        worker.signals.progress.connect(self.redraw_preview)
        worker.signals.finished.connect(self.drawing_complete)
        self.threadpool.start(worker)

    def draw_map(self, progress_callback):
        '''
        Draws the image.
        '''
        self.image = Image.open(BLANK_PATH)
        draw = ImageDraw.Draw(self.image)
        draw.font = ImageFont.truetype(FONT_PATH, 42)
        text_color = (0, 0, 0)

        for station, edit in self.station_edit.items():
            value = edit.getInt()
            for region in station_regions[station]:
                # filling area with color
                x, y = region_coords[region]
                fill_color = value_to_color(value)
                ImageDraw.floodfill(self.image, (x, y), fill_color)
                # drawing the text
                info_to_display = (region, value, value_to_class(value))
                text = '\n'.join(map(str, info_to_display))
                draw.multiline_text((x, y), text=text, fill=text_color, anchor='mm', align='center')
                # callback to redraw preview
                progress_callback.emit(ImageQt(self.image))

    def redraw_preview(self, image: ImageQt):
        '''
        Redraws preview from given image.
        '''
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image.scaledToHeight(self.preview_image_height)))

    def drawing_complete(self):
        '''
        Handling end of drawing process; after it do the follows:
        1) Saving created image.
        2) Closing image file handler.
        3) Enabling buttonShowImage.
        4) Enabling buttonSubmit.
        '''
        today = datetime.date.today()
        self.image_name = IMAGE_NAME_TEMPLATE.format(day=today.day, month=today.month, year=today.year)
        self.image.save(self.image_name, 'PNG')  # 1
        self.image.close()  # 2
        self.buttonShowImage.setEnabled(True)  # 3
        self.buttonSubmit.setEnabled(True)  # 4

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_settings()
        super().closeEvent(event)

    def save_settings(self):
        '''
        Saves current window geometry.
        '''
        self.settings.setValue("geometry", self.saveGeometry())

    def restore_settings(self):
        '''
        Restores last window geometry.
        '''
        self.restoreGeometry(self.settings.value("geometry", type=QtCore.QByteArray))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())

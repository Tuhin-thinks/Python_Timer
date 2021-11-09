import os
import sys
import typing

from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia
from progressbar import QRoundProgressBar

TIME_COUNT = 60 * 6
SOUND_FILE = os.path.join("sound", "tick_sound_small.wav")


# sound_file_url = QtCore.QUrl.fromLocalFile(SOUND_FILE)
# content = QtMultimedia.QMediaContent(sound_file_url)
# player = QtMultimedia.QMediaPlayer()
# player.setMedia(content)
# player.setVolume(100)


class HomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()

        self.setWindowTitle("Circular Timer")

        self.central_widget = QtWidgets.QWidget(self)
        self.resize(QtCore.QSize(560, 560))
        self.setCentralWidget(self.central_widget)

        self.grid_layout1 = QtWidgets.QGridLayout(self.central_widget)
        self.central_widget.setLayout(self.grid_layout1)

        # ------------------- CREATE PROGRESS BAR -------------------------
        self.progress_bar = QRoundProgressBar(self.central_widget)
        self.progress_bar.decimals = 0
        self.progress_bar.setFixedSize(300, 300)
        self.progress_bar.setDataPenWidth(3)
        self.progress_bar.set_outline_pen_width(3)
        self.progress_bar.setDonutThicknessRatio(0.85)
        self.progress_bar.setDecimals(1)
        self.progress_bar.set_format("%p")
        # self.bar.resetFormat()
        self.progress_bar.set_null_position(90)
        self.progress_bar.value = 0
        self.progress_bar.setBarStyle(QRoundProgressBar.StylePie)

        # set color gradient
        self.progress_bar.setDataColors([(0., QtGui.QColor.fromRgb(255, 51, 51)),
                                         (0.5, QtGui.QColor.fromRgb(204, 0, 0)),
                                         (1., QtGui.QColor.fromRgb(92, 7, 7))])

        self.grid_layout1.addWidget(self.progress_bar)
        # --------------------- PROGRESSBAR END --------------------------

        self.push_button_start = QtWidgets.QPushButton("start", self.central_widget)
        self.grid_layout1.addWidget(self.push_button_start)

        self.push_button_start.clicked.connect(self.start_timer)
        # self.play_tick()

    def play_tick(self):
        self.sound = QtMultimedia.QSoundEffect()
        self.sound.setSource(QtCore.QUrl.fromLocalFile(SOUND_FILE))
        self.sound.setLoopCount(QtMultimedia.QSoundEffect.Infinite)
        self.sound.setVolume(100)
        self.sound.play()

    def start_timer(self):
        self.time_count = 0
        # set progressbar value and range
        self.progress_bar.set_range(0, TIME_COUNT)
        self.progress_bar._value = 0.0
        self.progress_bar.info_trail_str = " seconds"

        self.update_data()  # call first time for immediate response
        self.play_tick()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

        self.push_button_start.setDisabled(True)

    def check_time(self):
        if self.time_count >= TIME_COUNT:
            print("Timer stopped")
            self.timer.stop()
            self.value_animation.stop()
            self.progress_bar.value = TIME_COUNT
            self.push_button_start.setDisabled(False)
            self.sound.stop()
        self.update()

    def update_data(self):
        self.time_count += 1.0

        # self.play_tick()

        self.value_animation = QtCore.QPropertyAnimation(self.progress_bar, b'value')
        self.value_animation.setStartValue(self.time_count - 1)
        self.value_animation.setEndValue(self.time_count)
        self.value_animation.setDuration(1000)
        self.value_animation.setLoopCount(5)
        self.value_animation.setEasingCurve(QtCore.QEasingCurve.Linear)
        self.value_animation.start()

        self.check_time()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = HomeWindow()
    w.show()
    sys.exit(app.exec())

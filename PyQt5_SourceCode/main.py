import os
import sys

from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia

from progressbar import QRoundProgressBar

SOUND_FILE = os.path.join("sound", "tick_sound_small.wav")


class HomeWindow(QtWidgets.QMainWindow):
    def __init__(self, time_choices=None):
        super(HomeWindow, self).__init__()

        self.time_count = 0
        self.timer_max_duration = 1 * 60  # to store timer duration in minutes

        if not time_choices:
            self.time_choices = []
        else:
            self.time_choices = time_choices

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
        self.progress_bar.set_null_position(90)
        self.progress_bar.value = 0
        self.progress_bar.setBarStyle(QRoundProgressBar.StylePie)

        # set color gradient
        self.progress_bar.setDataColors([(0., QtGui.QColor.fromRgb(255, 51, 51)),
                                         (0.5, QtGui.QColor.fromRgb(204, 0, 0)),
                                         (1., QtGui.QColor.fromRgb(92, 7, 7))])

        # --------------------- PROGRESSBAR END --------------------------

        self.push_button_start = QtWidgets.QPushButton("start", self.central_widget)

        self.frame_top = QtWidgets.QFrame(self)
        self.frame_top.setMaximumHeight(100)
        self.frame_top.setObjectName("frame_top")
        self.frame_top.setStyleSheet("#frame_top{\n"
                                     "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 "
                                     "rgba(180, 230, 255, 255), "
                                     "stop:1 rgba(255, 255, 255, 255));\n "
                                     "border-radius: 15px;}")
        # set timer duration
        self.combobox_time = QtWidgets.QComboBox(self.frame_top)
        self.combobox_time.addItems(
            [str(x) + " minutes" for x in self.time_choices]
        )
        self.combobox_time.setMaximumWidth(120)
        self.label_1 = QtWidgets.QLabel("Select Timer duration", self.frame_top)
        self.label_1.setMaximumSize(200, 20)
        self.grid_layout2 = QtWidgets.QGridLayout(self.frame_top)

        # add combobox and label to frame grid layout
        self.grid_layout2.addWidget(self.label_1, 0, 0, 1, 1)
        self.grid_layout2.addWidget(self.combobox_time, 0, 1, 1, 1)

        # add widgets to main layout
        self.grid_layout1.addWidget(self.frame_top, 1, 0, 1, 1)
        self.grid_layout1.addWidget(self.progress_bar)
        self.grid_layout1.addWidget(self.push_button_start)

        # signals
        self.push_button_start.clicked.connect(self.start_timer)
        self.combobox_time.currentIndexChanged[int].connect(self.change_time_duration)

    @QtCore.pyqtSlot(int)
    def change_time_duration(self, index):
        time = self.time_choices[index]
        self.timer_max_duration = time * 60

    def play_tick(self):
        self.sound = QtMultimedia.QSoundEffect()
        self.sound.setSource(QtCore.QUrl.fromLocalFile(SOUND_FILE))
        self.sound.setLoopCount(QtMultimedia.QSoundEffect.Infinite)
        self.sound.setVolume(100)
        self.sound.play()

    def start_timer(self):
        # reset time count everytime before start of timer
        self.time_count = 0

        # set progressbar value and range
        self.progress_bar.set_range(0, self.timer_max_duration)
        self.progress_bar._value = 0.0  # set progressbar current value
        self.progress_bar.info_trail_str = " seconds"

        self.update_data()  # call first time for immediate response
        self.play_tick()  # start playing the continuous sound once timer has started

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

        # disable controls
        self.frame_top.setDisabled(True)
        self.push_button_start.setDisabled(True)

    def check_time(self):
        if self.time_count >= self.timer_max_duration:
            print("Timer stopped")

            # stop timer, animation & sound
            self.timer.stop()
            self.value_animation.stop()
            self.sound.stop()

            # set timer display value to max (due to animation the timer display value, lags!)
            self.progress_bar.value = self.timer_max_duration

            # enable controls
            self.push_button_start.setDisabled(False)
            self.frame_top.setDisabled(False)

            # delete animation and timer
            self.value_animation.deleteLater()
            self.timer.deleteLater()

        self.update()

    def update_data(self):
        """Update timer data using animation creating a smooth display"""
        self.time_count += 1.0

        self.value_animation = QtCore.QPropertyAnimation(self.progress_bar, b'value')
        self.value_animation.setStartValue(self.time_count - 1)
        self.value_animation.setEndValue(self.time_count)
        self.value_animation.setDuration(1000)
        self.value_animation.setLoopCount(5)
        self.value_animation.setEasingCurve(QtCore.QEasingCurve.Linear)
        self.value_animation.start()

        # check time elapsed after every time update, to stop when required
        self.check_time()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # TODO: add functionality to select custom defined time from UI
    w = HomeWindow(
        [1, 2, 5, 10, 15, 20, 30, 45, 60]  # all measures are in minutes
    )
    w.show()
    sys.exit(app.exec())

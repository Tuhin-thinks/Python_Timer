import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from progressbar import QRoundProgressBar


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
        self.progress_bar.set_value(0)
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

    def start_timer(self):
        self.time_count = 0
        # set progressbar value and range
        self.progress_bar.set_range(0, 100)
        self.progress_bar.set_value(0)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

        self.push_button_start.setDisabled(True)

    def update_data(self):
        self.time_count += 1

        if self.time_count >= 100:
            self.timer.stop()
            self.push_button_start.setDisabled(False)

        self.progress_bar.set_value(self.time_count)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = HomeWindow()
    w.show()
    sys.exit(app.exec())

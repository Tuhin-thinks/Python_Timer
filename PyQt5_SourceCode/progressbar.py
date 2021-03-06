"""
Source code taken from https://stackoverflow.com/questions/33577068/any-pyqt-circular-progress-bar
Updated for PyQt5.
"""
import math
from typing import Union
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtProperty


class QRoundProgressBar(QtWidgets.QWidget):
    StyleDonut = 1
    StylePie = 2
    StyleLine = 3

    c_font = QtGui.QFont("Ubuntu Thin", 15, 50)
    info_trail_str = ""
    info_head = "–"

    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    UF_VALUE = 1
    UF_PERCENT = 2
    UF_MAX = 4

    def __init__(self, parent=None):
        super(QRoundProgressBar, self).__init__(parent=parent)

        self.minValue = 0
        self.maxValue = 100
        self._value = 0.0

        self.nullPosition = self.PositionTop
        self.barStyle = self.StyleDonut
        self.outlinePenWidth = 1
        self.dataPenWidth = 1
        self.rebuildBrush = False
        self.format = "%p%"
        self.decimals = 1
        self.updateFlags = self.UF_PERCENT
        self.gradientData = []
        self.donutThicknessRatio = 0.75

    @property
    def custom_font(self):
        return self.c_font

    @custom_font.setter
    def custom_font(self, font: 'QtGui.QFont'):
        self.c_font = font

    def set_range(self, min_: int, max_: int):
        self.minValue = min_
        self.maxValue = max_

        if self.maxValue < self.minValue:
            self.maxValue, self.minValue = self.minValue, self.maxValue

        if self._value < self.minValue:
            self._value = self.minValue
        elif self._value > self.maxValue:
            self._value = self.maxValue

        if not self.gradientData:
            self.rebuildBrush = True
        self.update()

    def set_min(self, min_value: int):
        self.set_range(min_value, self.maxValue)

    def set_max(self, max_value: int):
        self.set_range(self.minValue, max_value)

    @pyqtProperty(float)
    def value(self):
        return self._value

    @value.setter
    def value(self, val: float):
        if self._value <= val:
            if val < self.minValue:
                self._value = self.minValue
            elif val > self.maxValue:
                self._value = self.maxValue
            else:
                self._value = val
            self.update()

    def set_null_position(self, position):
        if position != self.nullPosition:
            self.nullPosition = position
            if not self.gradientData:
                self.rebuildBrush = True
            self.update()

    def setBarStyle(self, style):
        if style != self.barStyle:
            self.barStyle = style
            self.update()

    def set_outline_pen_width(self, penWidth):
        if penWidth != self.outlinePenWidth:
            self.outlinePenWidth = penWidth
            self.update()

    def setDataPenWidth(self, penWidth):
        if penWidth != self.dataPenWidth:
            self.dataPenWidth = penWidth
            self.update()

    def setDataColors(self, stopPoints):
        if stopPoints != self.gradientData:
            self.gradientData = stopPoints
            self.rebuildBrush = True
            self.update()

    def set_format(self, format_str: str):
        if format_str != self.format:
            self.format = format_str
            self.valueFormatChanged()

    def reset_format(self):
        self.format = ''
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.decimals:
            self.decimals = count
            self.valueFormatChanged()

    def setDonutThicknessRatio(self, val):
        self.donutThicknessRatio = max(0., min(val, 1.))
        self.update()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QtCore.QRectF(1, 1, outerRadius - 2, outerRadius - 2)

        buffer = QtGui.QImage(outerRadius, outerRadius, QtGui.QImage.Format_ARGB32)
        buffer.fill(0)

        p = QtGui.QPainter(buffer)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # background
        self.drawBackground(p, buffer.rect())

        # base circle
        self.drawBase(p, baseRect)

        # data circle
        arcStep = 360.0 / (self.maxValue - self.minValue) * self._value
        self.drawValue(p, baseRect, self._value, arcStep)

        # center circle
        innerRect, innerRadius = self.calculateInnerRect(outerRadius)
        self.drawInnerBackground(p, innerRect)

        # text
        self.drawText(p, innerRect, innerRadius, self._value)

        # finally draw the bar
        p.end()

        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, self.palette().window())

    def drawBase(self, p, baseRect):
        bs = self.barStyle
        if bs == self.StyleDonut:
            p.setPen(QtGui.QPen(self.palette().shadow().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StylePie:
            p.setPen(QtGui.QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(self.palette().base())
            p.drawEllipse(baseRect)
        elif bs == self.StyleLine:
            p.setPen(QtGui.QPen(self.palette().base().color(), self.outlinePenWidth))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawEllipse(
                baseRect.adjusted(self.outlinePenWidth / 2, self.outlinePenWidth / 2, -self.outlinePenWidth / 2,
                                  -self.outlinePenWidth / 2))

    def drawValue(self, painter: 'QtGui.QPainter', base_rect: 'QtCore.QRectF', value: Union[float, int],
                  step: Union[float, int]):
        # nothing to draw
        if value == self.minValue:
            return

        # for Line style
        if self.barStyle == self.StyleLine:
            painter.setPen(QtGui.QPen(self.palette().highlight().color(), self.dataPenWidth))
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawArc(
                base_rect.adjusted(self.outlinePenWidth / 2, self.outlinePenWidth / 2, -self.outlinePenWidth / 2,
                                   -self.outlinePenWidth / 2),
                self.nullPosition * 16, - step * 16)
            return

        # for Pie and Donut styles
        dataPath = QtGui.QPainterPath()
        dataPath.setFillRule(QtCore.Qt.WindingFill)

        # pie segment outer
        dataPath.moveTo(base_rect.center())
        dataPath.arcTo(base_rect, self.nullPosition, -step)
        dataPath.lineTo(base_rect.center())

        painter.setBrush(self.palette().highlight())
        painter.setPen(QtGui.QPen(self.palette().shadow().color(), self.dataPenWidth))
        painter.drawPath(dataPath)

    def calculateInnerRect(self, outerRadius):
        # for Line style
        if self.barStyle == self.StyleLine:
            innerRadius = outerRadius - self.outlinePenWidth
        else:  # for Pie and Donut styles
            innerRadius = outerRadius * self.donutThicknessRatio

        delta = (outerRadius - innerRadius) / 2.
        innerRect = QtCore.QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawInnerBackground(self, p, innerRect):
        if self.barStyle == self.StyleDonut:
            p.setBrush(self.palette().alternateBase())

            cmod = p.compositionMode()
            p.setCompositionMode(QtGui.QPainter.CompositionMode_Source)

            p.drawEllipse(innerRect)

            p.setCompositionMode(cmod)

    def drawText(self, p, innerRect, innerRadius, value):
        def conditional_pen():
            if (remaining_value / self.maxValue) > 0.58:
                return QtCore.Qt.red
            elif (remaining_value / self.maxValue) > 0.40:
                return QtCore.Qt.black
            else:
                return QtCore.Qt.white

        if not self.format:
            return

        text = self.valueToText(value)
        remaining_value = self.maxValue - value

        f = self.custom_font
        f.setPixelSize(innerRadius * 1.0 / len(text))
        p.setFont(f)

        p.setPen(self.palette().text().color())
        p.drawText(innerRect, QtCore.Qt.AlignCenter, text)

        # create the info rect (to show the remaining time information etc.)

        # # calculate rect dimensions
        bottom_left, bottom_right = innerRect.bottomLeft(), innerRect.bottomRight()
        rect_height = 50
        top_y = bottom_left.y() - rect_height
        bottom_y = bottom_left.y()
        left_x = bottom_left.x()
        right_x = bottom_right.x()

        # # draw the rect
        infoRect = QtCore.QRectF(QtCore.QPointF(left_x, top_y), QtCore.QPointF(right_x, bottom_y))

        # variable font-color changing using preset conditions
        p.setPen(conditional_pen())

        f2 = self.custom_font
        f2.setPixelSize(20)

        if remaining_value <= 0:
            f2.setBold(True)
            p.setFont(f2)
            p.drawText(infoRect, QtCore.Qt.AlignCenter, "Time's up!")
        elif remaining_value == self.maxValue:
            p.setFont(f2)
            p.drawText(infoRect, QtCore.Qt.AlignCenter, f"--:--")
        else:
            p.setFont(f2)
            p.drawText(infoRect, QtCore.Qt.AlignCenter, f"{self.info_head}{remaining_value:.02f}{self.info_trail_str}")

        self.update()

    def valueToText(self, value: Union[float, int]):
        """function to convert a float or int value to string with specific format"""

        textToDraw = self.format

        # format_string = '{' + ':.{}f'.format(self.decimals) + '}'
        format_string = "{:02d}"

        if self.updateFlags & self.UF_VALUE:
            textToDraw = textToDraw.replace("%v", format_string.format(value))

        if self.updateFlags & self.UF_PERCENT:
            percent = (value - self.minValue) / (self.maxValue - self.minValue) * 100.0
            textToDraw = textToDraw.replace("%p", format_string.format(math.ceil(percent)))

        if self.updateFlags & self.UF_MAX:
            m = self.maxValue - self.minValue + 1
            textToDraw = textToDraw.replace("%m", format_string.format(m))

        return textToDraw

    def valueFormatChanged(self):
        self.updateFlags = 0

        if "%v" in self.format:
            self.updateFlags |= self.UF_VALUE

        if "%p" in self.format:
            self.updateFlags |= self.UF_PERCENT

        if "%m" in self.format:
            self.updateFlags |= self.UF_MAX

        self.update()

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            dataBrush = QtGui.QConicalGradient()
            dataBrush.setCenter(0.5, 0.5)
            dataBrush.setCoordinateMode(QtGui.QGradient.StretchToDeviceMode)

            for pos, color in self.gradientData:
                dataBrush.setColorAt(1.0 - pos, color)

            # angle
            dataBrush.setAngle(self.nullPosition)

            p = self.palette()
            p.setBrush(QtGui.QPalette.Highlight, dataBrush)
            self.setPalette(p)

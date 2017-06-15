class ColorPicker(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.setObjectName("colorPicker")

        self.gradient = GradientSquare()
        self.hue = GradientHue()
        self.color = None


        sideLayout = QtGui.QVBoxLayout()
        sideLayout.setContentsMargins(0, 0, 0, 0)
        self.colorRect = QtGui.QFrame()
        self.colorRect.setFixedSize(85, 50)

        self.red = QtGui.QSpinBox()
        self.red.setRange(0, 255)
        self.green = QtGui.QSpinBox()
        self.green.setRange(0, 255)
        self.blue = QtGui.QSpinBox()
        self.blue.setRange(0, 255)
        self.hexa = QtGui.QLineEdit()
        self.hexa.setMaximumWidth(65)
        self.red.setStyle(QtGui.QStyleFactory.create("Windows"))
        self.green.setStyle(QtGui.QStyleFactory.create("Windows"))
        self.blue.setStyle(QtGui.QStyleFactory.create("Windows"))

        self.OK = QtGui.QPushButton("OK")

        formLayout = QtGui.QFormLayout()
        formLayout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop )
        formLayout.setContentsMargins(0, 0, 0, 0)
        formLayout.addRow("R:", self.red)
        formLayout.addRow("G:", self.green)
        formLayout.addRow("B:", self.blue)
        formLayout.addRow("#:", self.hexa)
        formLayout.addRow(self.OK)

        sideLayout.addWidget(self.colorRect)
        sideLayout.addLayout(formLayout)



        self.layout().addWidget(self.gradient)
        self.layout().addWidget(self.hue)
        self.layout().addLayout(sideLayout)

        self.gradient.valueChanged.connect(self.colorChanged)
        self.hue.valueChanged.connect(self.hueChanged)
        self.adjustSize()
        self.colorChanged()

    def colorChanged(self):
        self.color = self.gradient.color
        self.colorRect.setStyleSheet("background-color: "+self.color.name()+";")
    def hueChanged(self):
        self.gradient.changeGradientColor(self.hue.color)

    def setColor(self, color):
        self.hue.setPos(color)
        self.gradient.setPos(color)

    # def paintEvent(self, event):
    #     painter = QtGui.QPainter()
    #     painter.begin(self)
    #     painter.setRenderHint(QtGui.QPainter.Antialiasing)
    #     painter.fillRect(event.rect(), QtGui.QBrush(QtGui.QColor("#4a4a4a")))
    #     painter.end()


class GradientHue(QtGui.QWidget):
    valueChanged = CustomSignal().valueChanged
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedSize(20, 200)

        self.color = None

        # Signal
        self.signal = CustomSignal()
        self.valueChanged = self.signal.valueChanged

        self.cursorPos = QtCore.QPoint(0, 0)

        self.colorGradient = QtGui.QLinearGradient(0, self.height(), 0, 0)
        self.colorGradient.setColorAt(0, QtGui.QColor(255, 0, 0))
        self.colorGradient.setColorAt(1.0/6, QtGui.QColor(255, 255, 0))
        self.colorGradient.setColorAt(2.0/6, QtGui.QColor(0, 255, 0))
        self.colorGradient.setColorAt(3.0/6, QtGui.QColor(0, 255, 255))
        self.colorGradient.setColorAt(4.0/6, QtGui.QColor(0, 0, 255))
        self.colorGradient.setColorAt(5.0/6, QtGui.QColor(255, 0, 255))
        self.colorGradient.setColorAt(1, QtGui.QColor(255, 0, 0))

        self.cursor = QtGui.QLabel()
        self.cursor.setPixmap(QtGui.QPixmap("./icons/line.png"))
        self.cursor.setParent(self)
        self.cursor.setFixedSize(self.cursor.sizeHint())
        self.cursorPadding = QtCore.QPoint(0, self.cursor.height() / 2)

        self.moveCursor(self.cursorPos)

    def mousePressEvent(self, event):
        self.moveCursor(event.pos())

    def mouseMoveEvent(self, event):
        self.moveCursor(event.pos())

    def getHue(self):
        hue = 1-(self.cursorPos.y()/float(self.height()))
        if hue >= 1:
            hue = 0.0

        return hue

    def setPos(self, color):
        pos = int((1-color.hsvHueF())*self.height())
        self.cursorPos.setY(pos)
        self.moveCursor(self.cursorPos)

    def moveCursor(self, newPosition):
        # Force the cursor to stay inside of the gradient widget
        if newPosition.y() < 0:
            newPosition.setY(0)
        if newPosition.y() > self.height():
            newPosition.setY(self.height())
        newPosition.setX(0)

        self.cursorPos = newPosition
        self.cursor.move(newPosition - self.cursorPadding)
        self.color = QtGui.QColor.fromHsvF(self.getHue(), 1, 1)

        self.valueChanged.emit()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.colorGradient)
        painter.end()

class GradientSquare(QtGui.QWidget):
    valueChanged = CustomSignal().valueChanged
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedSize(200, 200)

        # Signal
        self.signal = CustomSignal()
        self.valueChanged = self.signal.valueChanged

        self.color = None
        self.hueColor = None

        self.cursorPos = QtCore.QPoint(0, 0)

        # Base gradient setup
        self.colorGradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
        self.colorGradient.setColorAt(0.01, QtGui.QColor(255, 255, 255))
        self.satGradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        self.satGradient.setColorAt(0.01, QtGui.QColor(255, 255, 255, 0))
        self.satGradient.setColorAt(0.99, QtGui.QColor(0, 0, 0))
        self.changeGradientColor(QtGui.QColor("#ff0000"))

        # The cursor imgs
        self.whiteCircle = QtGui.QPixmap("./icons/circle-white.png")
        self.BlackCircle = QtGui.QPixmap("./icons/circle-black.png")

        # Cursor object
        self.cursor = QtGui.QLabel()
        self.cursor.setPixmap(self.BlackCircle)
        self.cursor.setParent(self)
        self.cursor.setFixedSize(self.cursor.sizeHint())
        self.cursorPadding = QtCore.QPoint(self.cursor.sizeHint().width() / 2, self.cursor.sizeHint().height() / 2)
        self.moveCursor(self.cursorPos)

    def mousePressEvent(self, event):
        self.moveCursor(event.pos())

    def mouseMoveEvent(self, event):
        self.moveCursor(event.pos())

    def changeGradientColor(self, color):
        self.hueColor = color.hsvHueF()
        self.colorGradient.setColorAt(0.99, color)
        self.update()
        self.color = self.getColor()
        self.valueChanged.emit()

    def getColor(self):
        s = self.cursorPos.x()/float(self.width())
        v = 1-(self.cursorPos.y()/float(self.height()))
        return QtGui.QColor.fromHsvF(self.hueColor, s, v)

    def setPos(self, color):

        x = int(color.saturationF()*self.width())
        y = int((1-color.valueF())*self.width())

        pos = QtCore.QPoint(x, y)

        self.moveCursor(pos)

    def moveCursor(self, newPosition):
        # Force the cursor to stay inside of the gradient widget
        if newPosition.x() < 0:
            newPosition.setX(0)
        if newPosition.y() < 0:
            newPosition.setY(0)
        if newPosition.x() > self.width():
            newPosition.setX(self.width())
        if newPosition.y() > self.height():
            newPosition.setY(self.height())

        # Change cursor color depending of the height position
        if newPosition.y() > (self.height() / 3):
            self.cursor.setPixmap(self.whiteCircle)
        else:
            self.cursor.setPixmap(self.BlackCircle)

        # Change the cursor position (the picker position) value
        self.cursorPos = newPosition

        # Move the Label to the new position with the offset
        self.cursor.move(self.cursorPos - self.cursorPadding)
        self.color = self.getColor()

        self.valueChanged.emit()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.colorGradient)
        painter.fillRect(self.rect(), self.satGradient)
        painter.end()

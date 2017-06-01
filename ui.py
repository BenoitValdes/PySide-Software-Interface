from PySide import QtCore, QtGui
import os, re

with open("./main.css","r") as f:
    css = f.read()

def getCssValue(ids, attr = None, css = css):
    displayLine = False
    content = []
    for line in css.split("\n"):
        if (isinstance(ids, tuple) or isinstance(ids, list)) and all(x in line for x in ids):
            displayLine = True

        if isinstance(ids, str) and ids in line:
            displayLine = True

        if "}" in line:
            displayLine = False

        if displayLine:
            if attr and attr in line:
                value = re.findall("[A-Za-z0-9-_#]+", line)[1:]
                if len(value) == 1:
                    value = value[0]
                return value
            elif not attr:
                content.append(line+"\n")
    if content:
        return content

class IconButton(QtGui.QPushButton):
    def __init__(self, img, color = (255, 0, 0), size = None):
        QtGui.QPushButton.__init__(self)
        pix = QtGui.QPixmap(img)
        alpha =  pix.alphaChannel()
        self.customIcon = QtGui.QPixmap(pix.size())
        if len(color) == 6:
            color = tuple(int(color[i:i+2], 16) for i in (0, 2 ,4))

        self.customIcon.fill(QtGui.QColor(color[0], color[1], color[2]))
        self.customIcon.setAlphaChannel(alpha)
        self.setIcon(QtGui.QIcon(self.customIcon))
        self.setFlat(True)
        if not size:
            size = (pix.width(), pix.height())
        self.setFixedSize(size[0], size[1])
        self.setCursor(QtCore.Qt.PointingHandCursor)

class ContainerWidget(QtGui.QWidget):
    def __init__(self, parent, widget):
        QtGui.QWidget.__init__(self, parent)
        self.button = QtGui.QPushButton("Close Overlay")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.topLayout = QtGui.QHBoxLayout()
        self.text = QtGui.QLabel("MyLabel")
        self.close = IconButton("./icons/close.png", (30, 30, 30), (16, 16))

        self.widgets = []

        self.contentLayout = QtGui.QStackedLayout()
        self.widgets.append(widget)

        self.setLayout(QtGui.QVBoxLayout())
        self.topLayout.addWidget(self.text)
        self.topLayout.addWidget(self.close)
        self.contentLayout.addWidget(self.widgets[-1])
        self.layout().addLayout(self.topLayout)
        self.layout().addLayout(self.contentLayout)

        self.close.clicked.connect(self.hideOverlay)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 10, 10)
        painter.fillPath(path, QtGui.QColor(getCssValue("popup", "background-color")))
        painter.end()

    def hideOverlay(self):
        self.parent().hide()

    def replaceWidget(self, widget):
        self.widgets.append(widget)
        self.contentLayout.addWidget(self.widgets[-1])
        self.contentLayout.setCurrentWidget(widget)
        self.widgets.pop(0)


class Overlay(QtGui.QWidget):
    def __init__(self, parent, widget):
        QtGui.QWidget.__init__(self, parent)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

        self.colours = getCssValue("overlay", "background-color")

        self.widget = ContainerWidget(self, widget)
        self.widget.adjustSize()
        self.hide()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(event.rect(), QtGui.QBrush(QtGui.QColor(int(self.colours[0]), int(self.colours[1]), int(self.colours[2]), int(self.colours[3]))))
        painter.end()

    def resizeEvent(self, event):
        position_x = (self.parent().geometry().width()-self.widget.geometry().width())/2
        position_y = (self.parent().geometry().height()-self.widget.geometry().height())/2
        self.widget.move(position_x, position_y)
        event.accept()

    def switchWidget(self, widget):
        self.widget.replaceWidget(widget)

class TopBar(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedHeight(50)
        self.setObjectName("topBar")
        self.setAutoFillBackground(True)

        self.menuBtn = IconButton("./icons/bars.png", "ffffff")
        self.search = SearchBar()
        self.settingsBtn = IconButton("./icons/cog.png", "ffffff")

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(10,0,10,0)
        self.layout().addWidget(self.menuBtn)
        self.layout().addWidget(self.search)
        self.layout().addWidget(self.settingsBtn)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class SearchBar(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setObjectName("searchBar")

        # To be not select the search input by default
        invisible = QtGui.QLineEdit()
        invisible.setFixedWidth(0)

        self.input = QtGui.QLineEdit()
        self.input.setPlaceholderText("xxxx-xxxx")
        self.input.setMinimumSize(10, 35)
        self.input.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.button = IconButton("./icons/search.png", "eeeeee", (40, 35))

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().addWidget(invisible)
        self.layout().addWidget(self.input)
        self.layout().addWidget(self.button)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class BuildButton(QtGui.QWidget):
    def __init__(self, txt = "Clarisse 3.5"):
        QtGui.QWidget.__init__(self)
        self.setObjectName("buildBtn")
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.label = QtGui.QLabel(txt)

        self.addBtn = IconButton("./icons/plus.png", "ffffff", (30, 30))
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.addBtn)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class CustomSignal(QtCore.QObject):
    clicked = QtCore.Signal()

class RevButton(QtGui.QWidget):
    signal = CustomSignal()
    def __init__(self, txt = "Clarisse 3.5"):
        QtGui.QWidget.__init__(self)
        self.setObjectName("revBtn")
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.label = QtGui.QLabel(txt)

        self.addBtn = IconButton("./icons/chevron-right.png", "ffffff", (30, 30))
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.addBtn)

        self.setCursor(QtCore.Qt.PointingHandCursor)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

    def mousePressEvent(self, QMouseEvent):
        print "clicked"
        self.signal.clicked.emit()

    def connect(self, function):
        # print function
        pass

class Menu(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.state = True
        self.setVisible(self.state)
        self.setObjectName("menu")
        self.setFixedWidth(200)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        # The project Button
        self.projectButton = QtGui.QPushButton("Add Project")
        self.projectButton.setFlat(True)
        self.projectButton.setObjectName("projectBtn")
        self.projectButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.layout().addWidget(self.projectButton)

        # The Build Button
        self.projectButton = BuildButton()
        self.layout().addWidget(self.projectButton)

        self.buttons = []
        for i in range(3):
            self.buttons.append(RevButton("Rev 2145"+str(i+1)))
            self.layout().addWidget(self.buttons[-1])

        self.layout().addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class Settings(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.state = False
        self.setVisible(False)
        self.setObjectName("settings")
        self.setFixedWidth(150)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class PlaceHolder(QtGui.QWidget):
    def __init__(self, color):
        QtGui.QWidget.__init__(self)
        self.setMinimumSize(100, 100)
        css="""
        QWidget{
            background-color: #"""+color+"""
        }
        """
        self.setStyleSheet(css)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)


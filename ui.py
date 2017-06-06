from PySide import QtCore, QtGui
import os, re, time

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- CSS
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
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

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Custom Widgets
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

class CustomSignal(QtCore.QObject):
    clicked = QtCore.Signal()

class CustomIcon(QtGui.QPixmap):
    def __init__(self, img, color = (255, 255, 255), size = None):
        pix = QtGui.QPixmap(img)
        alpha =  pix.alphaChannel()
        if len(color) == 6:
            color = tuple(int(color[i:i+2], 16) for i in (0, 2 ,4))

        QtGui.QPixmap.__init__(self, pix.size())

        self.fill(QtGui.QColor(color[0], color[1], color[2]))
        self.setAlphaChannel(alpha)

class IconButton(QtGui.QPushButton):
    def __init__(self, img, color = (255, 0, 0), size = None):
        QtGui.QPushButton.__init__(self)
        pix = CustomIcon(img, color, size)
        self.setIcon(QtGui.QIcon(pix))
        self.setFlat(True)
        if not size:
            size = (pix.width(), pix.height())
        self.setFixedSize(size[0], size[1])
        self.setCursor(QtCore.Qt.PointingHandCursor)

class PaintedWidget(QtGui.QWidget):
    def __init__(self, parent, objectName):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName(objectName)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class FlatButton(QtGui.QPushButton):
    def __init__(self, txt):
        QtGui.QPushButton.__init__(self, txt)
        self.setObjectName("button")
        self.setFlat(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)

class UnitTestCategory(QtGui.QWidget):
    def __init__(self, infos):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.header = PaintedWidget(None, "utCategory")
        self.header.setLayout(QtGui.QHBoxLayout())
        self.header.layout().setContentsMargins(10, 0, 10, 0)
        self.header.layout().addWidget(QtGui.QLabel(infos["rev"]+" - Unit Test"))

        self.layout().addWidget(self.header)
"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Overlay/Popup
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

class ContainerWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.button = QtGui.QPushButton("Close Overlay")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.topLayout = QtGui.QHBoxLayout()
        self.title = QtGui.QLabel("MyLabel")
        self.title.setObjectName("title")
        self.close = IconButton("./icons/close-1.png", getCssValue("title", "color")[1:])

        self.widgets = []

        self.contentLayout = QtGui.QStackedLayout()
        self.widgets.append(QtGui.QWidget())

        self.setLayout(QtGui.QVBoxLayout())
        self.topLayout.addWidget(self.title)
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
        self.title.setText(self.widgets[-1].widgetName)
        self.adjustSize()
        self.parent().setGoodPosition()


class Overlay(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

        self.colours = getCssValue("overlay", "background-color")

        self.widget = ContainerWidget(self)
        self.widget.adjustSize()
        self.hide()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(event.rect(), QtGui.QBrush(QtGui.QColor(int(self.colours[0]), int(self.colours[1]), int(self.colours[2]), int(self.colours[3]))))
        painter.end()

    def resizeEvent(self, event):
        self.setGoodPosition()
        event.accept()

    def switchWidget(self, widget):
        self.widget.replaceWidget(widget)

        # Set main window minimum size depending on the content of the overlay
        width = self.widget.width()
        height = self.widget.height()
        self.parent().setMinimumSize(width+50, height+50)

    def mousePressEvent(self, QMouseEvent):
        if not self.widget.underMouse():
            self.hide()

    def setGoodPosition(self):
        position_x = (self.parent().geometry().width()-self.widget.geometry().width())/2
        position_y = (self.parent().geometry().height()-self.widget.geometry().height())/2
        self.widget.move(position_x, position_y)

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Top menu
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
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
        self.layout().addWidget(QtGui.QLabel(""))
        # self.layout().addWidget(self.settingsBtn)

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

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Left Menu
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
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

class RevButton(QtGui.QWidget):
    def __init__(self, txt = "Clarisse 3.5"):
        QtGui.QWidget.__init__(self)
        self.setFixedHeight(int(getCssValue("revBtn", "height")))
        self.setObjectName("revBtn")
        self.setCursor(QtCore.Qt.PointingHandCursor)

        # Signal
        self.signal = CustomSignal()
        self.clicked = self.signal.clicked

        # Widgets
        self.label = QtGui.QLabel(txt)
        self.icon = QtGui.QLabel("")
        self.icon.setObjectName("icon")
        self.openPix = CustomIcon("./icons/chevron-down.png", "ffffff", (30, 30))
        self.closePix = CustomIcon("./icons/chevron-right.png", "ffffff", (30, 30))
        self.icon.setPixmap(self.closePix)
        self.icon.setAlignment(QtCore.Qt.AlignRight)

        # Layout
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.icon)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

    def changePixmap(self, state):
        if state:
            self.icon.setPixmap(self.openPix)
        else:
            self.icon.setPixmap(self.closePix)

class SubMenuButton(QtGui.QWidget):
    def __init__(self, txt = "Clarisse 3.5"):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(0)
        self.height = 0

        self.buttons = []
        for name in ["UNIT TEST", "BUILD TEST", "BUILD TEST HD"]:
            self.buttons.append(QtGui.QPushButton(name))
            self.buttons[-1].setFlat(True)
            self.buttons[-1].setObjectName("subMenuBtn")
            self.buttons[-1].clicked.connect(self.setContent)
            self.layout().addWidget(self.buttons[-1])


        self.height = len(self.buttons) * int(getCssValue("subMenuBtn", "height")[:-2])

    def setContent(self):
        mainWindow = self.window()
        btnName = self.sender().text()
        if btnName == "UNIT TEST":
            mainWindow.changeContent(UTWidget(self))
        if btnName == "BUILD TEST":
            mainWindow.changeContent(BTWidget(self))
        if btnName == "BUILD TEST HD":
            mainWindow.changeContent(BTWidget(self, True))

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class RevWidget(QtGui.QWidget):
    def __init__(self, txt = "Rev XXXXXX"):
        QtGui.QWidget.__init__(self)
        self.setObjectName("revWidget")
        self.active = False
        self.txt = txt

        self.revBtn = RevButton(self.txt)
        self.submenu = SubMenuButton()

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.revBtn)
        self.layout().addWidget(self.submenu)

        self.revBtn.clicked.connect(self.slot)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

    def slot(self):
        self.window().left_menu.displaySubmenu(self)

    def activate(self, state):
        self.active = state
        if self.active:
            self.submenu.setFixedHeight(self.submenu.height)
            self.revBtn.changePixmap(self.active)
        else:
            self.submenu.setFixedHeight(0)
            self.revBtn.changePixmap(self.active)

class Menu(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.state = True
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
        self.buildBtn = BuildButton()
        self.layout().addWidget(self.buildBtn)

        # The Rev Buttons (inside a scroll Area)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.content = PaintedWidget(self.scrollArea, "menu")
        self.scrollLayout = QtGui.QVBoxLayout(self.content)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)

        self.menuItem = []
        for i in range(3):
            self.menuItem.append(RevWidget("Rev 2145"+str(i+1)))
            self.scrollLayout.addWidget(self.menuItem[-1])

        self.scrollLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

        self.layout().addWidget(self.scrollArea)
        self.content.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.content)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

    def displaySubmenu(self, current):
        start_time = time.time()
        for item in self.menuItem:
            if not item == current:
                item.activate(False)

        if current.active:
            current.activate(False)
        else:
            current.activate(True)

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Content widgets
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
class BTWidget(QtGui.QWidget):
    def __init__(self, parent, hd = False):
        QtGui.QWidget.__init__(self)
        self.setMinimumSize(100, 100)
        self.revWidget = parent.parent()
        self.name = self.revWidget.txt


        self.setLayout(QtGui.QHBoxLayout())
        if hd:
            self.layout().addWidget(QtGui.QLabel(self.name+" - BUILD TEST HD"))

        else:
            self.layout().addWidget(QtGui.QLabel(self.name+" - BUILD TEST"))


    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class UTWidget(QtGui.QWidget):
    def __init__(self, parent, name = ""):
        QtGui.QWidget.__init__(self)
        self.setMinimumSize(100, 100)
        self.revWidget = parent.parent()
        self.name = self.revWidget.txt


        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(UnitTestCategory({"rev":self.name}))



    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class SearchResultWidget(QtGui.QWidget):
    def __init__(self, currentRev, text):
        QtGui.QWidget.__init__(self)
        self.setMinimumSize(100, 100)
        if currentRev:
            txt = 'Looking for "'+text+'" in '+currentRev
        else:
            txt = "No rev selected..."

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(QtGui.QLabel(txt))

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Popup widgets
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
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
    def __init__(self, color, name = ""):
        QtGui.QWidget.__init__(self)
        self.setMinimumSize(100, 100)
        css="""
        QWidget{
            background-color: #"""+color+"""
        }
        """
        self.setStyleSheet(css)
        self.widgetName = name

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class ProjectPreference(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setObjectName("projectPrefs")
        # self.setFixedSize(300, 300)
        self.setMinimumWidth(500)
        self.widgetName = "Project Preferences"

        # Widgets
        itemDelegate = QtGui.QStyledItemDelegate()

        loadLabel = QtGui.QLabel("Load existing project")
        loadList = QtGui.QComboBox()
        loadList.setStyle(QtGui.QStyleFactory.create("Windows"))
        loadList.setItemDelegate(itemDelegate)
        for i in range(42):
            loadList.addItem("plop")
        loadButton = FlatButton("Load")
        loadButton.setMaximumWidth(100)

        createLabel = QtGui.QLabel("Create new project")
        createList = QtGui.QComboBox()
        createList.setStyle(QtGui.QStyleFactory.create("Windows"))
        createList.setItemDelegate(itemDelegate)
        for i in range(42):
            createList.addItem("plop")
        createButton = FlatButton("Create")
        createButton.setMaximumWidth(100)

        # Layouts
        self.setLayout(QtGui.QVBoxLayout())
        loadLayout = QtGui.QHBoxLayout()
        createLayout = QtGui.QHBoxLayout()

        loadLayout.addWidget(loadList)
        loadLayout.addWidget(loadButton)
        createLayout.addWidget(createList)
        createLayout.addWidget(createButton)

        self.layout().addWidget(loadLabel)
        self.layout().addLayout(loadLayout)
        self.layout().addWidget(createLabel)
        self.layout().addLayout(createLayout)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

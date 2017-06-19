from PySide import QtCore, QtGui
import os, re, time, webbrowser

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
    valueChanged = QtCore.Signal()

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
    def __init__(self, parent = None, objectName = ""):
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


class Tag(QtGui.QFrame):
    def __init__(self, name = ""):
        QtGui.QFrame.__init__(self)
        self.setObjectName("tag")
        self.setLayout(QtGui.QVBoxLayout())
        self.setProperty("type", "")
        # self.layout().setContentsMargins(0, 5, 0, 5)

        self.value = QtGui.QLabel("0")
        self.value.setObjectName("value")
        self.value.setAlignment(QtCore.Qt.AlignCenter)

        self.name = QtGui.QLabel(name)
        self.name.setAlignment(QtCore.Qt.AlignCenter)

        self.layout().addWidget(self.value)
        self.layout().addWidget(self.name)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setColor(name)

    def setColor(self, name):
        if name == "SUCCEED":
            self.setProperty("type", "succeed")
        if name == "FAILURE":
            self.setProperty("type", "failure")
        if name == "ERROR":
            self.setProperty("type", "error")
        if name == "UNTESTED":
            self.setProperty("type", "untested")

class ResizableWidget(QtGui.QScrollArea):
    def __init__(self, widget):
        QtGui.QScrollArea.__init__(self)
        self.setWidgetResizable(True)
        self.widget = widget
        self.setWidget(self.widget)

class Mantis(QtGui.QLabel):
    def __init__(self, name = ""):
        QtGui.QLabel.__init__(self)
        self.setFixedSize(50, 20)

        self.state = "new"
        self.name = str(name)
        self.setProperty("state", self.state)

        self.setObjectName("mantis")
        self.setText(self.name)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, QMouseEvent):
        url = "http://wiki.isotropix.net/mantis/view.php?id="+self.name
        print url
        webbrowser.open(url)

    def changeState(self, name):
        self.state = name
        self.setProperty("state", self.state)



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

        self.utWidget = None
        self.btWidget = None
        self.btHdWidget = None


        self.buttons = []
        for name in ["UNIT TEST", "GRAPHIC TEST", "PERFORMANCE TEST"]:
            self.buttons.append(QtGui.QPushButton(name))
            self.buttons[-1].setFlat(True)
            self.buttons[-1].setObjectName("subMenuBtn")
            self.buttons[-1].clicked.connect(self.setContent)
            self.layout().addWidget(self.buttons[-1])


        self.height = len(self.buttons) * int(getCssValue("subMenuBtn", "height")[:-2])

    def setContent(self):
        mainWindow = self.window()
        if self.sender() == self.buttons[0]:
            if not self.utWidget:
                self.utWidget = ResizableWidget(UTWidget(self))
            mainWindow.changeContent(self.utWidget)
        if self.sender() == self.buttons[1]:
            if not self.btWidget:
                self.btWidget = BTWidget(self)
            mainWindow.changeContent(self.btWidget)
        if self.sender() == self.buttons[2]:
            if not self.btHdWidget:
                self.btHdWidget = BTWidget(self, True)
            mainWindow.changeContent(self.btHdWidget)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class RevWidget(QtGui.QWidget):
    def __init__(self, rev, path = ""):
        QtGui.QWidget.__init__(self)
        self.setObjectName("revWidget")
        self.active = False
        self.number = rev
        self.txt = "Rev "+str(self.number)
        self.path = path

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
        for i in [20348, 20602, 21484]:
            self.menuItem.append(RevWidget(str(i)))
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

    def addMenuItem(self, infos):
        alreadyThere = False
        for widget in self.menuItem:
            if widget.number == infos["rev"]:
                alreadyThere = True
        if not alreadyThere:
            self.menuItem.append(RevWidget(infos["rev"], infos["path"]))
            print self.menuItem[-1].path
            numbers = {}
            for widget in self.menuItem:
                numbers[widget.number] = widget
                widget.setParent(None)
            for i in sorted(numbers.keys()):
                pos = self.scrollLayout.count()-1
                self.scrollLayout.insertWidget(pos, numbers[i])

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
        self.setObjectName("content")


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
        self.setObjectName("plop")
        css="""
        #plop{
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


"""
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- Unit Test Widget
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
class UTWidget(PaintedWidget):
    # Main widget wich will contain all the data about UT

    def __init__(self, parent):
        PaintedWidget.__init__(self)
        self.revWidget = parent.parent()
        self.name = self.revWidget.txt
        self.setObjectName("content")

        self.selectedUT = {}

        self.mainHeader = UTHeader(self.name+" - Unit Test")
        self.mainContent = UnitTestContent()
        self.mainContent.layout().setContentsMargins(0, 0, 0, 10)

        # Just for test
        for i in range(10):
            widget = UnitTestCategory({"name": "Unit Test "+str(i+1)})
            widget.content.layout().addWidget(UnitTest())
            widget.content.layout().addWidget(UnitTest())
            widget.content.layout().addWidget(UnitTest())
            widget.content.layout().addWidget(UnitTest())
            self.mainContent.layout().addWidget(widget)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().addWidget(self.mainHeader)
        self.layout().addWidget(self.mainContent)
        self.layout().addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))


        self.mainHeader.mousePressEvent(None)
        self.mainContent.changeState()
        self.mainHeader.freeze = True

    def updateSelected(self, catName, content):
        if not content:
            del self.selectedUT[catName]
        else:
            self.selectedUT[catName] = content

        if self.selectedUT:
            self.mainHeader.runSelected.show()
        else:
            self.mainHeader.runSelected.hide()
        print self.selectedUT

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class UTHeader(PaintedWidget):
    def __init__(self, label):
        PaintedWidget.__init__(self, objectName = "utHeader")
        self.clicked = CustomSignal().clicked
        self.open = False
        self.freeze = False
        self.setProperty("open", self.open)
        self.setFixedHeight(int(getCssValue("utHeader", "height")))
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(10, 5, 10, 5)

        self.title = QtGui.QLabel(label)
        self.run = FlatButton("RUN")
        self.run.setMaximumWidth(80)

        self.runSelected = FlatButton("RUN SELECTED")
        self.runSelected.setMaximumWidth(150)
        self.runSelected.hide()

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.runSelected)
        self.layout().addWidget(self.run)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, QMouseEvent):
        self.open = not self.open
        self.changeStyle("open", self.open)
        self.clicked.emit()

    def changeStyle(self, qproperty, value):
        if not self.freeze:
            self.setProperty(qproperty, value)
            self.style().polish(self)

class UnitTestContent(PaintedWidget):
    def __init__(self, parent = None):
        PaintedWidget.__init__(self, parent, "utContent")
        self.visible = False

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 10)
        self.setMaximumHeight(0)

        self.succeed = Tag("SUCCEED")
        self.failed = Tag("FAILURE")
        self.error = Tag("ERROR")
        self.untested = Tag("UNTESTED")

        reportLayout = QtGui.QHBoxLayout()
        reportLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        reportLayout.setContentsMargins(0, 0, 0, 0)
        reportLayout.setSpacing(0)
        reportLayout.addWidget(self.succeed)
        reportLayout.addWidget(self.failed)
        reportLayout.addWidget(self.error)
        reportLayout.addWidget(self.untested)

        self.layout().addLayout(reportLayout)

    def changeState(self):
        self.visible = not self.visible
        if self.visible:
            self.setMaximumHeight(999999)
            # self.show()
        else:
            self.setMaximumHeight(0)
            # self.hide()


class UnitTestCategory(QtGui.QWidget):
    def __init__(self, infos):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(10, 0, 10, 0)
        self.layout().setSpacing(0)

        self.selectedUT = []

        self.header = UTHeader(infos["name"])
        self.content = UnitTestContent()

        self.layout().addWidget(self.header)
        self.layout().addWidget(self.content)

        self.header.clicked.connect(self.content.changeState)

    def updateSelected(self, widget):
        if widget.selected and not widget in self.selectedUT:
            self.selectedUT.append(widget)
        elif not widget.selected and widget in self.selectedUT:
            self.selectedUT.pop(self.selectedUT.index(widget))

        if self.selectedUT:
            self.header.runSelected.show()
        else:
            self.header.runSelected.hide()

        self.parent().parent().updateSelected(self.header.title.text(), self.selectedUT)

class UnitTest(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setObjectName("unitTest")
        self.state = "untested"
        self.selected = False
        self.setProperty("state", self.state)

        self.label = QtGui.QLabel("UnitTest Name")
        self.run = FlatButton("RUN")
        self.run.setMaximumWidth(80)

        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(30, 0, 10, 0)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.run)

        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, QMouseEvent):
        key = QtGui.QApplication.keyboardModifiers()
        if key == QtCore.Qt.ControlModifier:
            self.selected = not self.selected
            self.parent().parent().updateSelected(self)
            self.changeStyle()
        else:
            self.window().displayOverlay(UnitTestInfos())

    def changeStyle(self):
        value = self.state
        if self.selected:
            value = "selected"
        self.setProperty("state", value)
        self.style().polish(self)
        self.style().polish(self.label)


    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)


class UnitTestInfos(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.widgetName = "Unit Test"
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.copyBtn = FlatButton("Copy script to Clipboard")

        topLayout = QtGui.QHBoxLayout()

        topLayout.addWidget(QtGui.QLabel("Created 25/04/2014 - Updated 24/05/2016"))
        topLayout.addWidget(self.copyBtn)

        self.description = QtGui.QLabel()
        self.description.setWordWrap(True)
        txt = '''<h2><span style="text-decoration: underline;">Description:</span></h2>
<p align= "justify">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris sed pellentesque purus. Vestibulum ac elit et augue cursus pharetra. Nullam vel elementum dui, a congue quam. Suspendisse elit massa, tempus vitae luctus ac, vestibulum non lectus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Integer ac purus gravida justo pharetra finibus a non quam. Nam eleifend dapibus arcu auctor cursus. Suspendisse sollicitudin sed dui eget egestas. Cras convallis finibus justo, a rutrum nisl dapibus eu. Aenean maximus blandit velit, quis porta orci interdum sit amet. In vitae elementum velit, sed dictum nulla. Phasellus lacinia non nulla eu dignissim.</p>
<h2><span style="text-decoration: underline;">Mantis:</span></h2>
        '''
        self.description.setText(txt)

        self.layout().addLayout(topLayout)
        self.layout().addWidget(self.description)
        self.layout().addWidget(Mantis(6245))

        self.copyBtn.clicked.connect(self.copyToClipboard)

    def copyToClipboard(self):
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText("Clipboard Text", mode=cb.Clipboard)

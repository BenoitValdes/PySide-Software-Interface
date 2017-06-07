from PySide import QtCore, QtGui
import sys, ui, time, subprocess, platform, os, re

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        # Window Config
        self.setObjectName("mainWindow")
        self.setStyleSheet(ui.css)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('QA Software')
        # self.move(3200, 658)
        self.resize(800, 500)

        # Widgets
        self.top_menu = ui.TopBar()
        self.left_menu = ui.Menu()
        self.settings = ui.Settings()
        self.content_widget = QtGui.QStackedWidget()
        self.content_widget.setObjectName("content")
        self.widgets = []
        self.widgets.append(ui.PlaceHolder("e6e6e6"))
        self.projectSettings = ui.ProjectPreference()

        # Layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.core_layout = QtGui.QHBoxLayout()
        self.core_layout.setContentsMargins(0,0,0,0)
        self.core_layout.setSpacing(0)

        self.main_layout.addWidget(self.top_menu)
        self.main_layout.addLayout(self.core_layout)
        self.core_layout.addWidget(self.left_menu)
        self.core_layout.addWidget(self.content_widget)
        self.core_layout.addWidget(self.settings)
        for widget in self.widgets:
            self.content_widget.addWidget(widget)

        self.setLayout(self.main_layout)
        self.overlay = ui.Overlay(self)

        # --- Connections ---------------------------------------------------------------------------------------------
        self.top_menu.menuBtn.clicked.connect(lambda: self.displayMenu(self.left_menu))
        # About search
        self.top_menu.search.input.editingFinished.connect(self.searchSlot)
        self.top_menu.search.button.clicked.connect(self.searchSlot)

        # About menu
        self.left_menu.projectButton.clicked.connect(lambda: self.displayOverlay(self.projectSettings))
        self.left_menu.buildBtn.addBtn.clicked.connect(self.addRev)

        # self.left_menu.buttons[0].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))
        # self.left_menu.buttons[1].clicked.connect(lambda: self.changeContent(placeHolder1))
        # self.left_menu.buttons[2].clicked.connect(lambda: self.changeContent(placeHolder2))

        # self.left_menu.buttons[0].clicked.connect(lambda: self.changeContent(0))
        # self.left_menu.buttons[1].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff0000")))
        # self.left_menu.buttons[2].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))

    def addRev(self):
        folder = QtGui.QFileDialog().getExistingDirectory()
        if platform.system() == "Darwin":
            cnode = folder+"/clarisse.app/Contents/MacOS/cnode"
            cnode = "\\ ".join(cnode.split(" "))
        else:
            cnode = folder+"cnode"
        proc = subprocess.Popen([cnode], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out:
            output = out
        else:
            output = err

        revNumber =  re.findall("#[0-9]*", output)[0][1:]
        path = cnode

        infos = {"rev": revNumber, "path": path}

        self.left_menu.addMenuItem(infos)




    def searchSlot(self):
        currentRev = None
        for rev in self.left_menu.menuItem:
            if rev.active:
                currentRev = rev.txt

        text = ""
        if isinstance(self.sender(), QtGui.QPushButton):
            text = self.sender().parent().input.text()
        elif isinstance(self.sender(), QtGui.QLineEdit):
            text = self.sender().text()

        searchWidget = ui.SearchResultWidget(currentRev, text)
        self.changeContent(searchWidget)

    def displayMenu(self, sender):
        sender.state = not sender.state
        sender.setVisible(sender.state)

    def changeContent(self, widget):
        if not widget in self.widgets:
            self.widgets.append(widget)
            widget = self.widgets[-1]
            self.content_widget.addWidget(widget)
        self.content_widget.setCurrentWidget(widget)

    def displayOverlay(self, widget=False):
        if widget:
            self.overlay.switchWidget(widget)
        self.overlay.show()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

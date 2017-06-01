from PySide import QtCore, QtGui
import sys, ui, time

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        # Window Config
        self.setObjectName("mainWindow")
        self.setStyleSheet(ui.css)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('QA Software')
        # self.move(3200, 658)
        self.resize(800, 500)

        # Widgets
        self.top_menu = ui.TopBar()
        self.left_menu = ui.Menu()
        self.settings = ui.Settings()
        placeHolder1 = ui.PlaceHolder("e6e6e6")
        placeHolder2 = ui.PlaceHolder("880000")

        # Layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.core_layout = QtGui.QHBoxLayout()
        self.core_layout.setContentsMargins(0,0,0,0)
        self.core_layout.setSpacing(0)
        self.content_layout = QtGui.QStackedLayout()
        self.content_layout.setObjectName("content")
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(0)

        self.main_layout.addWidget(self.top_menu)
        self.main_layout.addLayout(self.core_layout)
        self.core_layout.addWidget(self.left_menu)
        self.core_layout.addLayout(self.content_layout)
        self.core_layout.addWidget(self.settings)
        self.content_layout.addWidget(placeHolder1)
        self.content_layout.addWidget(placeHolder2)

        self.setLayout(self.main_layout)
        self.overlay = ui.Overlay(self, ui.PlaceHolder("ffff00"))

        # Connections
        self.top_menu.menuBtn.clicked.connect(lambda: self.displayMenu(self.left_menu))
        self.top_menu.settingsBtn.clicked.connect(lambda: self.displayMenu(self.settings))

        self.left_menu.buttons[0].signal.clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))

        # self.left_menu.buttons[0].clicked.connect(lambda: self.changeContent(0))
        # self.left_menu.buttons[1].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff0000")))
        # self.left_menu.buttons[2].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))

    @QtCore.Slot()
    def plop(self, txt = "plop"):
        print txt

    def displayMenu(self, sender):
        sender.state = not sender.state
        sender.setVisible(sender.state)

    def changeContent(self, index):
        self.content_layout.setCurrentIndex(index)

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

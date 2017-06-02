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
        self.move(3200, 658)
        self.resize(800, 500)

        # Widgets
        self.top_menu = ui.TopBar()
        self.left_menu = ui.Menu()
        self.settings = ui.Settings()
        self.content_widget = QtGui.QStackedWidget()
        self.widgets = []
        self.widgets.append(ui.PlaceHolder("e6e6e6"))

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
        self.overlay = ui.Overlay(self, ui.PlaceHolder("ffff00"))

        # --- Connections ---------------------------------------------------------------------------------------------
        self.top_menu.menuBtn.clicked.connect(lambda: self.displayMenu(self.left_menu))
        # About search
        self.top_menu.search.input.editingFinished.connect(self.searchSlot)
        self.top_menu.search.button.clicked.connect(self.searchSlot)

        # About menu
        self.left_menu.projectButton.clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff0000")))
        self.left_menu.buildBtn.addBtn.clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("FF00FF")))

        # self.left_menu.buttons[0].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))
        # self.left_menu.buttons[1].clicked.connect(lambda: self.changeContent(placeHolder1))
        # self.left_menu.buttons[2].clicked.connect(lambda: self.changeContent(placeHolder2))

        # self.left_menu.buttons[0].clicked.connect(lambda: self.changeContent(0))
        # self.left_menu.buttons[1].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff0000")))
        # self.left_menu.buttons[2].clicked.connect(lambda: self.displayOverlay(ui.PlaceHolder("ff00FF")))

    def searchSlot(self):
        # print self.sender().text()
        text = ""
        if isinstance(self.sender(), QtGui.QPushButton):
            text = self.sender().parent().input.text()
        elif isinstance(self.sender(), QtGui.QLineEdit):
            text = self.sender().text()

        print text

    def displayMenu(self, sender):
        sender.state = not sender.state
        sender.setVisible(sender.state)

    def changeContent(self, widget):

        self.content_widget.setCurrentWidget(index)

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
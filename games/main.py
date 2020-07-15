from PyQt5.QtWidgets import QApplication

from GameSelector import ControllerWindow

stylesheet = open( "style.qss", "r" ).read()
app = QApplication( [ ] )
window = ControllerWindow( None, stylesheet )
window.show()
app.exec_()

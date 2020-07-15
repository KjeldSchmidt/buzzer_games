from PyQt5.QtWidgets import QApplication

from GameSelector import GameSelector

app = QApplication( [ ] )
window = GameSelector()
window.setStyleSheet( open( "style.qss", "r" ).read() )
window.show()
app.exec_()

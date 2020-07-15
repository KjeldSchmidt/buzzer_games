from PyQt5.QtWidgets import QApplication

from GameSelector import GameSelector

app = QApplication( [ ] )
window = GameSelector()
window.show()
app.exec_()

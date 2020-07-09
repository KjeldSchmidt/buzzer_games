from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

app = QApplication( [ ] )
window = MainWindow()
window.show()
app.exec_()

import sys
from PyQt5.QtWidgets import QApplication
from gui.logger import logger
from gui.main_window import MainWindow


if __name__ == "__main__":
    logger
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

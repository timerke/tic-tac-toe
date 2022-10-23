import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


DIR_MEDIA: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")


def show_message(title: str, message: str) -> None:
    """
    Function displays message box with information.
    :param title: title;
    :param message: message.
    """

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setWindowIcon(QIcon(os.path.join(DIR_MEDIA, "icon.png")))
    msg_box.setText(message)
    msg_box.exec_()

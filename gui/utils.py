import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QPushButton


DIR_MEDIA: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")


def show_message(title: str, message: str, button_ok: bool = False) -> int:
    """
    Function displays message box with information.
    :param title: title;
    :param message: message.
    :return:
    """

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setWindowIcon(QIcon(os.path.join(DIR_MEDIA, "icon.png")))
    msg_box.setText(message)
    if button_ok:
        button_ok: QPushButton = QPushButton("OK")
        msg_box.addButton(button_ok, QMessageBox.AcceptRole)
        button_cancel: QPushButton = QPushButton("Отмена")
        msg_box.addButton(button_cancel, QMessageBox.RejectRole)
    return msg_box.exec()

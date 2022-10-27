import os
from typing import List, Optional, Tuple
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QLabel
from PyQt5.uic import loadUi
from gui import utils as ut


class ConnectionWindow(QDialog):
    """
    Class for selecting an adversary over a local network.
    """

    COLUMN_COUNT: int = 2
    login_set: pyqtSignal = pyqtSignal(str)
    opponent_selected: pyqtSignal = pyqtSignal(str)

    def __init__(self, player_login: Optional[str] = None) -> None:
        super().__init__()
        self._new_players: List[Tuple[str, str]] = []
        self._old_players: List[Tuple[str, str]] = []
        self._login: str = player_login
        self._init_ui()

    def _add_player_to_table(self, address: str, login: str) -> None:
        """
        Method adds new player to table.
        :param address: IP address of new player;
        :param login: new player login.
        """

        rows = self.table_widget.rowCount()
        for row in range(rows):
            if address == self.table_widget.cellWidget(row, 0).text():
                self.table_widget.cellWidget(row, 1).setText(login)
                return
        self.table_widget.setRowCount(rows + 1)
        self.table_widget.setCellWidget(rows, 0, QLabel(address))
        self.table_widget.setCellWidget(rows, 1, QLabel(login))

    def _init_table(self) -> None:
        """
        Method initializes table widget.
        """

        self.table_widget.setColumnCount(self.COLUMN_COUNT)
        self.table_widget.setHorizontalHeaderLabels(["IP адрес", "Логин"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.cellDoubleClicked.connect(self.select_opponent)

    def _init_ui(self) -> None:
        """
        Method initializes widgets on dialog window.
        """

        loadUi(os.path.join(ut.DIR_MEDIA, "connection_window.ui"), self)
        self.setWindowTitle("Найти соперника")
        self.setWindowIcon(QIcon(os.path.join(ut.DIR_MEDIA, "icon.png")))

        self.line_edit_login.returnPressed.connect(self.set_player_login)
        if self._login:
            self.line_edit_login.setText(self._login)
        self.button_set_login.clicked.connect(self.set_player_login)
        self.button_select_player.clicked.connect(self.select_opponent)
        self.button_cancel.clicked.connect(self.close)
        self._init_table()

    def _remove_player(self, address: str) -> None:
        """
        Method removes player with given IP address from table widget.
        :param address: IP address of player.
        """

        for row in range(self.table_widget.rowCount()):
            if self.table_widget.cellWidget(row, 0).text() == address:
                self.table_widget.removeRow(row)
                break

    @pyqtSlot(str, str)
    def add_player(self, address: str, login: str) -> None:
        """
        Slot adds new player.
        :param address: IP address of player;
        :param login: player login.
        """

        self._new_players.append((address, login))
        if (address, login) not in self._old_players:
            self._add_player_to_table(address, login)

    @pyqtSlot()
    def complete_revealing(self) -> None:
        new_addresses = np.array([item[0] for item in self._new_players])
        old_addresses = np.array([item[0] for item in self._old_players])
        removed_addresses = np.setdiff1d(old_addresses, new_addresses)
        for address in removed_addresses:
            self._remove_player(address)
        self._old_players = self._new_players

    @pyqtSlot()
    def select_opponent(self) -> None:
        """
        Slot selects opponent.
        """

        row = self.table_widget.currentRow()
        widget = self.table_widget.cellWidget(row, 0)
        if widget:
            self.opponent_selected.emit(widget.text())
            self.close()

    @pyqtSlot()
    def set_player_login(self) -> None:
        """
        Slot sets login for player.
        """

        self.login_set.emit(self.line_edit_login.text())

    @pyqtSlot()
    def start_revealing(self) -> None:
        self._new_players = []

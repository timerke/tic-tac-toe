import os
import random
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from game import ComputerPlayer, Game, Player
from gui import utils as ut


class MainWindow(QMainWindow):
    """
    Class for main window of application.
    """

    def __init__(self) -> None:
        super().__init__()
        self._game: Game = Game()
        self._game.game_over.connect(self.end_game)
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Method initializes widgets on main window.
        """

        loadUi(os.path.join(ut.DIR_MEDIA, "main_window.ui"), self)
        self.setWindowTitle("Крестики-нолики")
        self.setWindowIcon(QIcon(os.path.join(ut.DIR_MEDIA, "icon.png")))

        self.button_start_offline_game.clicked.connect(self.start_offline_game)
        self.button_start_game_with_computer.clicked.connect(self.start_game_with_computer)
        self.button_start_online_game.clicked.connect(self.start_online_game)

        cell_buttons = []
        for row in range(Game.ROWS_AND_COLUMNS):
            column_buttons = []
            for column in range(Game.ROWS_AND_COLUMNS):
                button = getattr(self, f"button_{row}_{column}")
                column_buttons.append(button)
                button.setEnabled(False)
            cell_buttons.append(column_buttons)
        self._game.set_buttons(cell_buttons)

    @pyqtSlot(int)
    def end_game(self, player_index: int) -> None:
        """
        Slot ends game.
        :param player_index: winner index.
        """

        if player_index == -1:
            message = "Ничья"
        else:
            message = f"Игрок #{player_index + 1} выиграл"
        ut.show_message("Информация", message)

    @pyqtSlot()
    def start_game_with_computer(self) -> None:
        """
        Slot starts game with computer.
        """

        id_for_player = random.randint(0, 1)
        players = (Player(0), ComputerPlayer(1)) if id_for_player == 0 else (ComputerPlayer(0), Player(1))
        self._game.start_game(*players)

    @pyqtSlot()
    def start_offline_game(self) -> None:
        """
        Slot starts offline game with other user.
        """

        player_1 = Player(0)
        player_2 = Player(1)
        self._game.start_game(player_1, player_2)

    @pyqtSlot()
    def start_online_game(self) -> None:
        """
        Slot starts online game.
        """

        pass

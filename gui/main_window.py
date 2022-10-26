import os
import random
import uuid
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QCloseEvent, QIcon, QResizeEvent
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from connection.server import Server
from game import ComputerPlayer, Game, Player
from gui import utils as ut
from gui.connection_window import ConnectionWindow
from revealer import RevealerClient, RevealerServer


class MainWindow(QMainWindow):
    """
    Class for main window of application.
    """

    def __init__(self) -> None:
        super().__init__()
        self._game: Game = Game()
        self._game.game_over.connect(self.end_game)
        self._id: str = uuid.uuid4()
        self._login: str = None
        self._connection_window: ConnectionWindow = ConnectionWindow(self._login)
        self._revealer_client: RevealerClient = RevealerClient()
        self._revealer_server: RevealerServer = RevealerServer()
        self._server: Server = Server()
        self._thread_for_server: QThread = QThread()
        self._init_ui()
        self._connect_signals()
        self._revealer_client.start()
        self._revealer_server.start()
        self._thread_for_server.start()

    def _connect_signals(self) -> None:
        """
        Method connects signals.
        """

        self._thread_for_server.setTerminationEnabled(True)
        self._server.moveToThread(self._thread_for_server)
        self._thread_for_server.started.connect(self._server.run)
        self._thread_for_server.finished.connect(self._server.close_server)

        self._revealer_client.setTerminationEnabled(True)
        self._revealer_client.player_found.connect(self._connection_window.add_player)
        self._revealer_client.search_completed.connect(self._connection_window.complete_revealing)
        self._revealer_client.search_started.connect(self._connection_window.start_revealing)
        self._revealer_server.setTerminationEnabled(True)

    def _init_ui(self) -> None:
        """
        Method initializes widgets on main window.
        """

        loadUi(os.path.join(ut.DIR_MEDIA, "main_window.ui"), self)
        self.setWindowTitle("Крестики-нолики")
        self.setWindowIcon(QIcon(os.path.join(ut.DIR_MEDIA, "icon.png")))

        self._connection_window.login_set.connect(self.set_login)

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Method handles main window close.
        :param event: close event.
        """

        self._revealer_client.quit()
        self._revealer_server.quit()
        self._thread_for_server.quit()
        super().closeEvent(event)

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Method handles resize of main window.
        :param event: resize event.
        """

        self._game.resize()
        super().resizeEvent(event)

    @pyqtSlot(str)
    def set_login(self, new_login: str) -> None:
        """
        Slot sets new login for player to play in local network.
        :param new_login: new login.
        """

        self._login = new_login
        self._revealer_server.set_login(self._login)

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

        self._connection_window.show()

import os
import random
import socket
import uuid
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent, QIcon, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from connection import Client, Server
from game import ComputerPlayer, Game, Player
from gui import utils as ut
from gui.connection_window import ConnectionWindow
from revealer import RevealerClient, RevealerServer


class MainWindow(QMainWindow):
    """
    Class for main window of application.
    """

    choice_made: pyqtSignal = pyqtSignal(socket.socket, str)

    def __init__(self) -> None:
        super().__init__()
        self._game: Game = Game()
        self._game.game_over.connect(self.end_game)
        self._id: str = uuid.uuid4()
        self._login: str = None
        self._connection_window: ConnectionWindow = ConnectionWindow(self._login)
        self._revealer_client: RevealerClient = RevealerClient()
        self._revealer_server: RevealerServer = RevealerServer()
        self._client: Client = Client()
        self._server: Server = Server()
        self._init_ui()
        self._connect_signals()
        self._revealer_client.start()
        self._revealer_server.start()
        self._client.start()
        self._server.start()

    def _connect_signals(self) -> None:
        """
        Method connects signals.
        """

        self._client.setTerminationEnabled(True)
        self._server.setTerminationEnabled(True)
        self._server.challenged.connect(self.handle_call_to_online_game)
        self._revealer_client.setTerminationEnabled(True)
        self._revealer_client.player_found.connect(self._connection_window.add_player)
        self._revealer_client.search_completed.connect(self._connection_window.complete_revealing)
        self._revealer_client.search_started.connect(self._connection_window.start_revealing)
        self._revealer_server.setTerminationEnabled(True)
        self._connection_window.login_set.connect(self.set_login)
        self._connection_window.opponent_selected.connect(self._client.start_game)

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Method handles main window close.
        :param event: close event.
        """

        self._revealer_client.quit()
        self._revealer_server.close_server()
        self._client.quit()
        self._server.close_server()
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

    @pyqtSlot(socket.socket)
    def handle_call_to_online_game(self, sock: socket.socket) -> None:
        """
        Slot handles call to start online game.
        :param sock: socket of the opponent who called to play online.
        """

        if self._game.game_in_progress:
            return
        if QMessageBox.AcceptRole == ut.show_message("Информация", f"Игрок {sock.getsockname()} бросил Вам вызов. "
                                                                   f"Хотите сыграть?", button_ok=True):
            choice = "Yes"
        else:
            choice = "No"
        self.choice_made.emit(sock, choice)

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

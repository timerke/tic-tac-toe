import logging
import socket
from PyQt5.QtCore import QThread
from revealer.params import REVEALER_HOST, REVEALER_PORT, SIZE


class RevealerServer(QThread):
    """
    Class for revealer server to send its information to other players.
    """

    def __init__(self) -> None:
        super().__init__()
        self._host: str = REVEALER_HOST
        self._port: int = REVEALER_PORT
        self._login: str = None
        self._socket: socket.socket = None
        self._stop: bool = False

    def close_server(self) -> None:
        """
        Method closes revealer server.
        """

        self._socket.close()
        logging.info("Revealer server was closed")

    def run(self) -> None:
        """
        Method runs server.
        """

        if not self.start_server():
            logging.error("Revealer server failed to start on port %d", self._port)
            return
        logging.info("Revealer server running on port %d", self._port)
        while not self._stop:
            try:
                data, address = self._socket.recvfrom(SIZE)
                if data.startswith(b"DISCOVER_TIC_TAC_TOE"):
                    self._socket.sendto(f"DISCOVER_TIC_TAC_TOE {self._login if self._login else ''}".encode("utf-8"),
                                        address)
            except Exception:
                pass

    def set_login(self, login: str) -> None:
        """
        Method sets login for player.
        :param login: login.
        """

        self._login = login

    def start_server(self) -> bool:
        """
        Method starts revealer server on some port.
        :return: True if server was started.
        """

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind((self._host, self._port))
            return True
        except Exception:
            return False

import socket
import time
from typing import Dict, Optional
from PyQt5.QtCore import QObject
from connection.messenger import Messenger


class Client(QObject):
    """
    Class for client.
    """

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self._host: str = host
        self._port: int = port
        self._messenger: Messenger = Messenger()
        self._socket: socket.socket = None

    def connect(self) -> None:
        """
        Method connects client to server.
        """

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((self._host, self._port))
        except ConnectionRefusedError:
            time.sleep(1)

    def process_message(self) -> Optional[Dict[str, str]]:
        """
        Method parses message from server.
        """

        try:
            return self._messenger.get_message(self._socket)
        except Exception:
            pass

    def send_message(self, message: Dict[str, str]) -> None:
        """
        Method sends messages to server.
        :param message: message to send.
        """

        try:
            self._messenger.send_message(self._socket, message)
        except Exception:
            pass

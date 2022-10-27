import logging
import queue
import socket
import time
from typing import Dict, Optional
from PyQt5.QtCore import pyqtSlot, QThread
from connection.messenger import Messenger
from connection.params import PORT


class Client(QThread):
    """
    Class for client.
    """

    def __init__(self) -> None:
        super().__init__()
        self._host: str = None
        self._port: int = PORT
        self._messenger: Messenger = Messenger()
        self._queue: queue.Queue = queue.Queue()
        self._socket: socket.socket = None

    def connect(self, host: str) -> None:
        """
        Method connects client to server.
        :param host: server address to connect.
        """

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((host, self._port))
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

    def run(self) -> None:
        while True:
            if not self._queue.empty():
                task = self._queue.get()
                try:
                    task()
                except Exception as exc:
                    logging.error(exc)
            time.sleep(0.5)

    def send_message(self, message: Dict[str, str]) -> None:
        """
        Method sends messages to server.
        :param message: message to send.
        """

        try:
            self._messenger.send_message(self._socket, message)
        except Exception:
            pass

    @pyqtSlot(str)
    def start_game(self, address: str) -> None:
        """
        Slot starts game with server with given IP address.
        :param address: server IP address.
        """

        self._queue.put(lambda: self.connect(address))
        self._queue.put(lambda: self.send_message({"MESSAGE": "Start game"}))

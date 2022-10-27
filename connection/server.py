import logging
import select
import socket
from typing import Dict, List
from PyQt5.QtCore import pyqtSignal, QThread
import connection.params as params
from connection.messenger import Messenger
from revealer.utils import get_ip_address


MESSAGE: str = "MESSAGE"
SOCKET: str = "SOCKET"


class Server(QThread):
    """
    Class for server.
    """

    MAX_CONNECTIONS: int = 5
    TIMEOUT: float = 0.1
    challenged: pyqtSignal = pyqtSignal(socket.socket)

    def __init__(self) -> None:
        super().__init__()
        self._host: str = get_ip_address()
        self._port: int = params.PORT
        self._messenger: Messenger = Messenger()
        self._socket: socket.socket = None
        self._stop: bool = False

    def _process_message(self, message: Dict[str, str], sock: socket.socket, tasks: List[Dict]) -> None:
        """
        Method processes message from client.
        :param message: message from client;
        :param sock: client socket;
        :param tasks: list of tasks for sending messages from server to clients.
        """

        if message.get("MESSAGE", None) == "Start game":
            self.challenged.emit(sock)

    def _get_messages(self, clients_to_read: List[socket.socket], clients: List[socket.socket], tasks: List[Dict]
                      ) -> None:
        """
        Method reads messages from clients.
        :param clients_to_read: list of client sockets to read messages from;
        :param clients: list of all client sockets;
        :param tasks: list of tasks for sending messages from server to clients.
        """

        for sock in clients_to_read:
            try:
                message = self._messenger.get_message(sock)
                self._process_message(message, sock, tasks)
            except Exception:
                clients.remove(sock)

    def _send_messages(self, clients: List[socket.socket], tasks: List[Dict]) -> None:
        """
        Method sends responses to clients that need it.
        :param clients: list of all client sockets;
        :param tasks: list of tasks for sending messages from server to clients.
        """

        while tasks:
            task = tasks[0]
            sock = task.get("SOCKET", None)
            message = task.get("MESSAGE", None)
            try:
                self._messenger.send_message(sock, message)
            except Exception:
                clients.remove(sock)
            finally:
                del tasks[0]

    def close_server(self) -> None:
        """
        Method closes server.
        """

        self._socket.close()
        logging.info("Server was closed")
        self.quit()

    @staticmethod
    def get_socket_param(sock: socket.socket) -> str:
        """
        Method returns socket IP address.
        :param sock: socket.
        :return: socket IP address.
        """

        return str(sock.getpeername())

    def start_server(self) -> bool:
        """
        Method starts server on some port.
        :return: True if server was started.
        """

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self._host, self._port))
            self._socket.listen(self.MAX_CONNECTIONS)
            self._socket.settimeout(self.TIMEOUT)
            return True
        except Exception:
            return False

    def run(self) -> None:
        """
        Method runs server.
        """

        if not self.start_server():
            logging.error("Server failed to start on port %d", self._port)
            return
        logging.info("Server running on port %d", self._port)
        clients = []
        tasks = []
        while not self._stop:
            try:
                client_socket, _ = self._socket.accept()
            except OSError:
                pass
            else:
                clients.append(client_socket)
            finally:
                clients_to_read = []
                try:
                    clients_to_read, _, errors = select.select(clients, clients, [], 0)
                except Exception:
                    pass
                self._get_messages(clients_to_read, clients, tasks)
                if tasks:
                    self._send_messages(clients, tasks)

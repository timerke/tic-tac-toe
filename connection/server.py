from typing import Dict, List
import select
import socket
from connection.messenger import Messenger


MESSAGE: str = "MESSAGE"
SOCKET: str = "SOCKET"


class Server:
    """
    Class for server.
    """

    MAX_CONNECTIONS: int = 5
    TIMEOUT: float = 0.1

    def __init__(self, host: str, port: int) -> None:
        self._host: str = host
        self._port: int = port
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

        pass

    def _read_messages(self, clients_to_read: List[socket.socket], all_clients: List[socket.socket], tasks: List[Dict]
                       ) -> None:
        """
        Method reads messages from clients.
        :param clients_to_read: list of client sockets to read messages from;
        :param all_clients: list of all client sockets;
        :param tasks: list of tasks for sending messages from server to clients.
        """

        for sock in clients_to_read:
            try:
                message = self._messenger.get_message(sock)
                self._process_message(message, sock, tasks)
            except Exception:
                all_clients.remove(sock)

    def _write_responses(self, all_clients: List[socket.socket], tasks: List[Dict]) -> None:
        """
        Method sends responses to clients that need it.
        :param all_clients: list of all client sockets;
        :param tasks: list of tasks for sending messages from server to clients.
        """

        while tasks:
            task = tasks[0]
            sock = task.get(SOCKET, None)
            message = task.get(MESSAGE, None)
            try:
                self._messenger.send_message(sock, message)
            except Exception:
                all_clients.remove(sock)
            finally:
                del tasks[0]

    def close(self) -> None:
        """
        Method closes server.
        """

        self._socket.close()

    @staticmethod
    def get_socket_param(sock: socket.socket) -> str:
        """
        Method returns socket IP address.
        :param sock: socket.
        :return: socket IP address.
        """

        return str(sock.getpeername())

    def open_server(self) -> None:
        """
        Method opens server.
        """

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(self.MAX_CONNECTIONS)
        self._socket.settimeout(self.TIMEOUT)

    def run(self) -> None:
        """
        Method runs server.
        """

        all_clients = []
        tasks = []
        while not self._stop:
            try:
                client_socket, _ = self._socket.accept()
            except OSError:
                pass
            else:
                all_clients.append(client_socket)
            finally:
                clients_to_read = []
                try:
                    clients_to_read, clients_to_write, errors = select.select(all_clients, all_clients, [], 0)
                except Exception:
                    pass
                self._read_messages(clients_to_read, all_clients, tasks)
                if tasks:
                    self._write_responses(all_clients, tasks)

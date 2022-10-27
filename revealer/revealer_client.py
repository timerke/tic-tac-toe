import logging
import re
import select
import socket
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import pyqtSignal, QThread
from revealer.params import REVEALER_PORT, SIZE
from revealer.utils import get_local_network_ip_addresses


class RevealerClient(QThread):
    """
    Class for revealer client to search other players in local network.
    """

    player_found: pyqtSignal = pyqtSignal(str, str)
    search_completed: pyqtSignal = pyqtSignal()
    search_started: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.stop_search: bool = False

    @staticmethod
    def _parse_login(data: bytes) -> str:
        """
        Method parses login from revealer server response.
        :param data: revealer server response.
        :return: player login on revealer server.
        """

        data = data.decode("utf-8")
        result = re.match(r"^DISCOVER_TIC_TAC_TOE (.*)$", data)
        if result:
            return result.group(1)
        return ""

    def _reveal(self, timeout: float = None) -> None:
        """
        Method detects available players in local network.
        :param timeout: max waiting time for responses.
        """

        waiting_time = 0.1
        if timeout is None:
            timeout = waiting_time
        timeout = timedelta(seconds=timeout)
        for local_address in get_local_network_ip_addresses():
            if self.stop_search:
                return
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto("DISCOVER_TIC_TAC_TOE".encode(), (local_address, REVEALER_PORT))
                    time_end = datetime.utcnow() + timeout
                    while True:
                        if self.stop_search:
                            return
                        time_now = datetime.utcnow()
                        time_left = (time_end - time_now).total_seconds()
                        if time_left < 0:
                            break
                        ready = select.select([sock], [], [], time_left)
                        if ready[0]:
                            data, address = sock.recvfrom(SIZE)
                            if data.startswith("DISCOVER_TIC_TAC_TOE".encode()):
                                self.player_found.emit(str(address[0]), self._parse_login(data))
            except Exception as exc:
                logging.debug("Failed to connect to address %s: %s", local_address, exc)

    def run(self) -> None:
        while True:
            self.search_started.emit()
            self._reveal()
            self.search_completed.emit()
            time.sleep(0.5)

    def stop(self) -> None:
        """
        Method stops searching.
        """

        self.stop_search = True

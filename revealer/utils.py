import logging
import os
import re
import socket
from typing import List


def get_ip_address() -> str:
    """
    Function returns IP address of server.
    :return: IP address.
    """

    ip = ""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    except Exception as exc:
        logging.error("Server can't get IP address: %s", exc)
    return ip


def get_local_network_ip_addresses() -> List[str]:
    """
    Function returns IP addresses in local network.
    :return: list of IP addresses in local network.
    """

    results = os.popen("arp -a").read().split("\n")
    ip_addresses = set()
    for result in results:
        match_result = re.match("^.* (?P<address>(\d{1,3}\.){3}\d{1,3}) .*$", result)
        if match_result:
            ip_addresses.add(match_result.group("address"))
    return list(ip_addresses)

import logging
import socket


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

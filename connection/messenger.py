import json
import socket
import struct
from typing import Dict, Optional


class Messenger:
    """
    Class for sending and receiving messages between a client and a server.
    """

    def get_message(self, sock: socket.socket) -> Dict[str, str]:
        """
        Method receives and decodes message from given socket.
        :param sock: socket.
        :return: message.
        """

        encoded_message = self.receive_entire_encoded_message(sock)
        if not isinstance(encoded_message, bytes):
            raise ValueError
        json_message = encoded_message.decode("utf-8")
        return json.loads(json_message)

    def receive_entire_encoded_message(self, sock: socket.socket) -> bytes:
        """
        Method for reading entire encoded message from given socket.
        :param sock: socket.
        :return: encoded message.
        """

        raw_message_length = self.receive_given_size_message(sock, 4)
        message_length = struct.unpack(">I", raw_message_length)[0]
        return self.receive_given_size_message(sock, message_length)

    @staticmethod
    def receive_given_size_message(sock: socket.socket, message_length: int) -> Optional[bytes]:
        """
        Method for reading a message of a given size from given socket.
        :param sock: socket;
        :param message_length: size of message.
        :return: message.
        """

        data = b""
        while len(data) < message_length:
            packet = sock.recv(message_length - len(data))
            if not packet:
                return None
            data += packet
        return data

    @staticmethod
    def send_message(sock: socket.socket, message: Dict[str, str]) -> None:
        """
        Method encodes and sends a message to socket. The protocol for sending messages
        is as follows. First, 4 bytes with the size of the message dictionary are sent,
        and then the message dictionary is sent.
        :param sock: socket;
        :param message: dictionary of message.
        """

        json_message = json.dumps(message)
        encoded_message = json_message.encode("utf-8")
        message = struct.pack(">I", len(encoded_message)) + encoded_message
        while message:
            sent_num = sock.send(message)
            message = message[sent_num:]

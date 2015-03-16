from spinnman.constants import CONNECTION_TYPE
from spinnman.connections.abstract_classes.abstract_udp_connection \
    import AbstractUDPConnection


import logging

logger = logging.getLogger(__name__)


class SpynnakerSenderConnection(AbstractUDPConnection):
    """ A connection for sending eieio messages to multiple places with a\
        single connection
    """

    def __init__(self, local_host=None, local_port=None):
        """
        :param local_host: Optional specification of the local hostname or\
                    ip address of the interface to bind to
        :type local_host: str
        :param local_port: Optional specification of the local port to bind to
        :type local_port: int
        """
        AbstractUDPConnection.__init__(
            self, local_host=local_host, local_port=local_port,
            remote_host=None, remote_port=None)

    def connection_type(self):
        CONNECTION_TYPE.UDP_IPTAG

    def supports_sends_message(self, message):
        return True

    def send_eieio_message(self, eieio_message, ip_address, port):
        data = eieio_message.convert_to_byte_array()
        self._socket.sendto(data, (ip_address, port))

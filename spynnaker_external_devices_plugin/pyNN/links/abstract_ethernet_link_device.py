#inhittance imports
from abc import ABCMeta

from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractEthernetLinkDevice(object):
    def __init__(self, port_id_in, port_id_out, ip_address):
        self._port_id_in = port_id_in
        self._port_id_out = port_id_out
        self._ip_address = ip_address

    @property
    def model_name(self):
        return "ExternalDevciceCommunicateaWithEthernetInterface:{}"\
            .format(self.label)
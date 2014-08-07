#inhittance imports
from abc import ABCMeta

from six import add_metaclass

from spynnaker_with_external_devices.pyNN.abstract_models.abstract_external_device import \
    AbstractExternalDevice


@add_metaclass(ABCMeta)
class AbstractSataLinkDevice(AbstractExternalDevice):
    def __init__(self, n_neurons, virtual_chip_coords, connected_node_coords,
                 connected_node_edge, label, max_atoms_per_core):
        AbstractExternalDevice.__init__(
            self, n_neurons, virtual_chip_coords, connected_node_coords,
            connected_node_edge, label, max_atoms_per_core)

    @property
    def model_name(self):
        return "ExternalDevciceCommunicateaWithSataInterface:{}"\
            .format(self.label)
__author__ = 'stokesa6'
from spynnaker_with_external_devices.pyNN.external_devices_models.abstract_external_device \
    import ExternalDevice


class ExternalCochleaDevice(ExternalDevice):

    def __init__(self, n_neurons, virtual_chip_coords,
                 connected_chip_coords, connected_chip_edge, max_atoms_per_core,
                 label=None):
        super(ExternalCochleaDevice, self).__init__(
            n_neurons, virtual_chip_coords, connected_chip_coords,
            connected_chip_edge, label=label,
            max_atoms_per_core=max_atoms_per_core)

    @property
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)
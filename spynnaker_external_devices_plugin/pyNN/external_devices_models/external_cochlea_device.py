__author__ = 'stokesa6'
from spynnaker_external_devices_plugin.pyNN.abstract_models.abstract_external_device \
    import AbstractExternalDevice


class ExternalCochleaDevice(AbstractExternalDevice):

    def __init__(self, n_neurons, virtual_chip_coords,
                 connected_chip_coords, connected_chip_edge, max_atoms_per_core,
                 machine_time_step, label=None):
        super(ExternalCochleaDevice, self).__init__(
            n_neurons, virtual_chip_coords, connected_chip_coords,
            connected_chip_edge, machine_time_step, label=label,
            max_atoms_per_core=max_atoms_per_core)

    @property
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)

    def is_external_device(self):
        return True

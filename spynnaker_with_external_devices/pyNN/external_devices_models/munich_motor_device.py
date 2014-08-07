from spynnaker_with_external_devices.pyNN.interfaces.abstract_munich_device import AbstractMunichDevice


class MunichMotorDevice(AbstractMunichDevice):
    MANAGEMENT_BIT = 0x400
    RATE_CODING_ACTUATORS_ENABLE = 0x40

    def __init__(self, n_neurons, virtual_chip_coords, connected_chip_coords,
                 connected_chip_edge, label=None, neuron_controlled=True):
        AbstractMunichDevice.__init__(
            self, n_neurons, virtual_chip_coords, connected_chip_coords,
            connected_chip_edge, label=label, max_atoms_per_core=1)

        self.neuron_controlled = neuron_controlled

    @property
    def model_name(self):
        return "external motor device"

    def get_commands(self, last_runtime_tic):
        return list()

from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex


class MunichMotorDevice(AbstractVirtualVertex):

    MANAGEMENT_BIT = 0x400
    RATE_CODING_ACTUATORS_ENABLE = 0x40

    def __init__(self, n_neurons, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None, neuron_controlled=True):

        AbstractVirtualVertex.__init__(
            self, n_neurons, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, label, max_atoms_per_core=1)

        self.neuron_controlled = neuron_controlled

    @property
    def model_name(self):
        return "external motor device"

    def is_virtual_vertex(self):
        return True
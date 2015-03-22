from spynnaker.pyNN.models.abstract_models.abstract_virtual_vertex \
    import AbstractVirtualVertex


class ExternalCochleaDevice(AbstractVirtualVertex):

    def __init__(self, n_neurons, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None):
        AbstractVirtualVertex.__init__(
            self, n_neurons, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, label=label,
            max_atoms_per_core=n_neurons)

    @property
    def model_name(self):
        return "ExternalCochleaDevice:{}".format(self.label)

    def is_virtual_vertex(self):
        return True

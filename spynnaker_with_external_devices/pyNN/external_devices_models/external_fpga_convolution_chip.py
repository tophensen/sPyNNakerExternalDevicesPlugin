from spynnaker_with_external_devices.pyNN.external_devices_models.abstract_FPGA_device import \
    AbstractFPGADevice


class ExternalFPGAConvolutionChip(AbstractFPGADevice):

    def __init__(self, n_neurons, virtual_chip_coords, connected_node_coords,
                 connected_node_edge, label, max_atoms_per_core):
        AbstractFPGADevice.__init__(
            self, n_neurons, virtual_chip_coords, connected_node_coords,
            connected_node_edge, label, max_atoms_per_core)


    def model_name(self):
        return "a external convolution chip which communicates via a fpga board"



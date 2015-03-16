import logging

from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from spynnaker.pyNN import exceptions
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand
from spynnaker.pyNN.models.abstract_models\
    .abstract_provides_outgoing_edge_constraints \
    import AbstractProvidesOutgoingEdgeConstraints
from spynnaker.pyNN.models.abstract_models.abstract_virtual_vertex \
    import AbstractVirtualVertex

from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.routing_info.key_and_mask import KeyAndMask


logger = logging.getLogger(__name__)


def get_y_from_fpga_retina(key, mode):
    if mode == 128:
        return key & 0x7f
    elif mode == 64:
        return key & 0x3f
    elif mode == 32:
        return key & 0x1f
    elif mode == 16:
        return key & 0xf
    else:
        return None


def get_x_from_fpga_retina(key, mode):
    if mode == 128:
        return (key >> 7) & 0x7f
    elif mode == 64:
        return (key >> 6) & 0x3f
    elif mode == 32:
        return (key >> 5) & 0x1f
    elif mode == 16:
        return (key >> 4) & 0xf
    else:
        return None


def get_spike_value_from_fpga_retina(key, mode):
    if mode == 128:
        return (key >> 14) & 0x1
    elif mode == 64:
        return (key >> 14) & 0x1
    elif mode == 32:
        return (key >> 14) & 0x1
    elif mode == 16:
        return (key >> 14) & 0x1
    else:
        return None


class ExternalFPGARetinaDevice(AbstractVirtualVertex,
                               AbstractSendMeMulticastCommandsVertex,
                               AbstractProvidesOutgoingEdgeConstraints):

    MODE_128 = "128"
    MODE_64 = "64"
    MODE_32 = "32"
    MODE_16 = "16"
    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"

    def __init__(
            self, mode, connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, polarity, machine_time_step,
            timescale_factor, spikes_per_second, ring_buffer_sigma,
            label=None, n_neurons=None):
        self._polarity = polarity
        fixed_n_neurons = n_neurons
        self._fixed_x = 5
        self._fixed_y = 0
        self._fixed_mask = None
        if mode == ExternalFPGARetinaDevice.MODE_128:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 128 * 128
            else:
                fixed_n_neurons = 128 * 128 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_64:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 64 * 64
            else:
                fixed_n_neurons = 64 * 64 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_32:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 32 * 32
            else:
                fixed_n_neurons = 32 * 32 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_16:
            if (polarity == ExternalFPGARetinaDevice.UP_POLARITY or
                    polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                fixed_n_neurons = 16 * 16
            else:
                fixed_n_neurons = 16 * 16 * 2
        else:
            raise exceptions.ConfigurationException("the FPGA retina does not "
                                                    "recongise this mode")

        if fixed_n_neurons != n_neurons and n_neurons is not None:
            logger.warn("The specified number of neurons for the FPGA retina"
                        " device has been ignored {} will be used instead"
                        .format(fixed_n_neurons))
        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, self._fixed_x, self._fixed_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, max_atoms_per_core=2048,
            label=label)
        AbstractSendMeMulticastCommandsVertex.__init__(self, commands=[
            MultiCastCommand(0, 0x0000FFFF, 0xFFFF0000, 1, 5, 100),
            MultiCastCommand(-1, 0x0000FFFE, 0xFFFF0000, 0, 5, 100)])

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):

        # Hack to use the neural modelling fixed mask
        mask = 0xFFFFF800
        vertex_slice = graph_mapper.get_subvertex_slice(
            partitioned_edge.pre_subvertex)

        # Should be one subedge for each 2048 atoms
        index = vertex_slice.lo_atom / 2048

        # The core index should be 8 higher for the up polarity
        if self._polarity == ExternalFPGARetinaDevice.UP_POLARITY:
            index += 8

        # The key is the virtual core number
        key = (self._virtual_chip_x << 24 | self._virtual_chip_y << 16 |
               index << 11)
        return list(
            [KeyAllocatorFixedKeyAndMaskConstraint([KeyAndMask(key, mask)])])

    @property
    def model_name(self):
        """
        name for debugs
        """
        return "external FPGA retina device"

    def is_virtual_vertex(self):
        return True

    def recieves_multicast_commands(self):
        return True

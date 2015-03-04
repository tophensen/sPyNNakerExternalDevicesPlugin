import logging

from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from spynnaker.pyNN import exceptions
from spynnaker.pyNN.models.abstract_models\
    .abstract_provides_keys_and_masks_vertex \
    import AbstractProvidesKeysAndMasksVertex
from spynnaker.pyNN.models.abstract_models.abstract_virtual_vertex \
    import AbstractVirtualVertex
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
                               AbstractProvidesKeysAndMasksVertex):

    MODE_128 = "128"
    MODE_64 = "64"
    MODE_32 = "32"
    MODE_16 = "16"
    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"

    def __init__(self, mode, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, polarity, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None, n_neurons=None):
        self._polarity = polarity
        fixed_n_neurons = n_neurons
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

        if fixed_n_neurons != n_neurons:
            logger.warn("The specified number of neurons for the FPGA retina"
                        "device has been ignored {} will be used instead"
                        .format(fixed_n_neurons))
        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, max_atoms_per_core=2048,
            label=label)

        self._commands_mask = 0xFFFFFBB8
        commands = list()
        commands.append({'t': 0, "cp": 1, 'key': None, 'key_prefix': 0xFFFF,
                         'payload': 1, 'repeat': 5, 'delay': 100})
        commands.append({'t': -1, "cp": 1, 'key': None, 'key_prefix': 0xFFFe,
                         'payload': 0, 'repeat': 5, 'delay': 100})
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, commands, self._commands_mask)

    def get_keys_and_masks_for_partitioned_edge(self, partitioned_edge,
                                                graph_mapper):

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
        key = (self._virtual_chip_x << 24 | self._virtual_chip_y << 16
               | index << 11)
        return [KeyAndMask(key, mask)]

    @property
    def model_name(self):
        """
        name for debugs
        """
        return "external FPGA retina device"

    @staticmethod
    def is_external_retina():
        return True

    def is_virtual_vertex(self):
        return True

    def recieves_multicast_commands(self):
        return True

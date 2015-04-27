from spynnaker.pyNN.models.abstract_models\
    .abstract_send_me_multicast_commands_vertex \
    import AbstractSendMeMulticastCommandsVertex
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from spynnaker.pyNN.models.abstract_models.abstract_virtual_vertex \
    import AbstractVirtualVertex
from spynnaker.pyNN import exceptions

from spinn_front_end_common.abstract_models\
    .abstract_outgoing_edge_same_contiguous_keys_restrictor\
    import AbstractOutgoingEdgeSameContiguousKeysRestrictor

from pacman.model.routing_info.key_and_mask import KeyAndMask
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand


# robot with 7 7 1
def get_x_from_robot_retina(key):
    return (key >> 7) & 0x7f


def get_y_from_robot_retina(key):
    return key & 0x7f


def get_spike_value_from_robot_retina(key):
    return (key >> 14) & 0x1


class PushBotRetinaDevice(AbstractVirtualVertex,
                         AbstractSendMeMulticastCommandsVertex,
                         AbstractOutgoingEdgeSameContiguousKeysRestrictor):

    # key codes for the robot retina
    MANAGEMENT_BIT = 0x80000000
    MANAGEMENT_MASK = 0x7FFFF000
    RETINA_ENABLE = 0x1
    RETINA_DISABLE = 0x0
    RETINA_KEY_SET = 0x2

    POLARITY_BIT = 0x1000
    
    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"

    def __init__(self, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None, n_neurons=None, polarity=None):

        if polarity is None:
            polarity = PushBotRetinaDevice.UP_POLARITY

        self._fixed_key = (virtual_chip_x << 24 | virtual_chip_y << 16)
        fixed_n_neurons = 128 * 128
        
        self._fixed_mask = 0xFFFFF000
        
        if polarity == PushBotRetinaDevice.UP_POLARITY:
            self._fixed_key |= PushBotRetinaDevice.POLARITY_BIT
        elif polarity == PushBotRetinaDevice.DOWN_POLARITY:
           pass
        else:
            assert False

        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, max_atoms_per_core=fixed_n_neurons,
            label=label)
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, self._get_commands())
        AbstractOutgoingEdgeSameContiguousKeysRestrictor.__init__(self)

        self._polarity = polarity
 
        if n_neurons != fixed_n_neurons and n_neurons is not None:
            print "Warning, the retina will have {} neurons".format(
                fixed_n_neurons)

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
        constraints = (AbstractOutgoingEdgeSameContiguousKeysRestrictor
                       .get_outgoing_edge_constraints(
                           self, partitioned_edge, graph_mapper))
        constraints.append(KeyAllocatorFixedKeyAndMaskConstraint(
            [KeyAndMask(self._fixed_key, self._fixed_mask)]))
        return constraints

    def _get_commands(self):
        """
        method that returns the commands for the retina external device
        """
        commands = list()

        # change the retina key it transmits with
        # (based off if its right or left)
        key_set_command = self.MANAGEMENT_BIT | self.RETINA_KEY_SET

        # to ensure populations receive the correct packets, this needs to be
        # different based on which retina
        key_set_payload = (self._virtual_chip_x << 24 |
                           self._virtual_chip_y << 16)

        commands.append(MultiCastCommand(
            0, key_set_command, self.MANAGEMENT_MASK, key_set_payload,
            5, 1000))

        # make retina enabled (dependant on if its a left or right retina
        enable_command = self.MANAGEMENT_BIT | self.RETINA_ENABLE
        commands.append(MultiCastCommand(
            0, enable_command, self.MANAGEMENT_MASK,
            (4 << 29) | (2 << 26),  # **YUCK** mystery flags
            5, 1000))

        # disable retina
        disable_command = self.MANAGEMENT_BIT | self.RETINA_DISABLE
        commands.append(MultiCastCommand(
            -1, disable_command, self.MANAGEMENT_MASK, 0, 
            5, 1000))

        return commands

    @property
    def model_name(self):
        return "external retina device at " \
               "with _polarity {}".format(self._polarity)

    def recieves_multicast_commands(self):
        return True

    def is_virtual_vertex(self):
        return True

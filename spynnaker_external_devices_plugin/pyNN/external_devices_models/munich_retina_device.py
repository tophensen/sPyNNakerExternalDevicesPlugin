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


class MunichRetinaDevice(AbstractVirtualVertex,
                         AbstractSendMeMulticastCommandsVertex,
                         AbstractOutgoingEdgeSameContiguousKeysRestrictor):

    # key codes for the robot retina
    MANAGEMENT_BIT = 0x400
    MANAGEMENT_MASK = 0xFFFFF800
    LEFT_RETINA_ENABLE = 0x45
    RIGHT_RETINA_ENABLE = 0x46
    LEFT_RETINA_DISABLE = 0x45
    RIGHT_RETINA_DISABLE = 0x46
    LEFT_RETINA_KEY_SET = 0x43
    RIGHT_RETINA_KEY_SET = 0x44

    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"

    LEFT_RETINA = "LEFT"
    RIGHT_RETINA = "RIGHT"

    def __init__(self, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, position, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None, n_neurons=None, polarity=None):

        if polarity is None:
            polarity = MunichRetinaDevice.MERGED_POLARITY

        self._fixed_key = (virtual_chip_x << 24 | virtual_chip_y << 16)
        self._fixed_mask = 0xFFFF8000
        if polarity == MunichRetinaDevice.UP_POLARITY:
            self._fixed_key |= 0x4000

        if polarity == MunichRetinaDevice.MERGED_POLARITY:

            # There are 128 x 128 retina "pixels" x 2 polarities
            fixed_n_neurons = 128 * 128 * 2
        else:

            # There are 128 x 128 retina "pixels"
            fixed_n_neurons = 128 * 128
            self._fixed_mask = 0xFFFFC000

        AbstractVirtualVertex.__init__(
            self, fixed_n_neurons, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, max_atoms_per_core=fixed_n_neurons,
            label=label)
        AbstractSendMeMulticastCommandsVertex.__init__(
            self, self._get_commands(position))
        AbstractOutgoingEdgeSameContiguousKeysRestrictor.__init__(self)

        self._polarity = polarity
        self._position = position

        if (self._position != self.RIGHT_RETINA and
           self._position != self.LEFT_RETINA):
            raise exceptions.ConfigurationException(
                "The external Retina does not recognise this _position")

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

    def _get_commands(self, position):
        """
        method that returns the commands for the retina external device
        """
        commands = list()

        # change the retina key it transmits with
        # (based off if its right or left)
        if position == self.RIGHT_RETINA:
            key_set_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_KEY_SET
        else:
            key_set_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_KEY_SET

        # to ensure populations receive the correct packets, this needs to be
        # different based on which retina
        key_set_payload = (self._virtual_chip_x << 24 |
                           self._virtual_chip_y << 16)

        commands.append(MultiCastCommand(
            0, key_set_command, self.MANAGEMENT_MASK, key_set_payload,
            5, 1000))

        # make retina enabled (dependant on if its a left or right retina
        if position == self.RIGHT_RETINA:
            enable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_ENABLE
        else:
            enable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_ENABLE
        commands.append(MultiCastCommand(
            0, enable_command, self.MANAGEMENT_MASK, 1, 5, 1000))

        # disable retina
        if position == self.RIGHT_RETINA:
            disable_command = self.MANAGEMENT_BIT | self.RIGHT_RETINA_DISABLE
        else:
            disable_command = self.MANAGEMENT_BIT | self.LEFT_RETINA_DISABLE

        commands.append(MultiCastCommand(
            -1, disable_command, self.MANAGEMENT_MASK, 0, 5, 1000))

        return commands

    @property
    def model_name(self):
        return "external retina device at " \
               "_position {} and _polarity {}".format(self._position,
                                                      self._polarity)

    def recieves_multicast_commands(self):
        return True

    def is_virtual_vertex(self):
        return True

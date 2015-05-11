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
#def get_x_from_robot_retina(key):
#    return (key >> 7) & 0x7f


#def get_y_from_robot_retina(key):
#    return key & 0x7f


#def get_spike_value_from_robot_retina(key):
#    return (key >> 14) & 0x1


class PushBotRetinaDevice(AbstractVirtualVertex,
                         AbstractSendMeMulticastCommandsVertex,
                         AbstractOutgoingEdgeSameContiguousKeysRestrictor):

    # key codes for the robot retina
    MANAGEMENT_MASK = 0xFFFFF800
    RETINA_ENABLE = 0x1
    RETINA_DISABLE = 0x0
    RETINA_KEY_SET = 0x2
    RETINA_RESET = 0x7
    
    SENSOR = 0x7F0
    SENSOR_SET_KEY = 0x0
    SENSOR_SET_PUSHBOT = 0x1

    UP_POLARITY = "UP"
    DOWN_POLARITY = "DOWN"
    MERGED_POLARITY = "MERGED"

    def __init__(self, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id, machine_time_step,
                 timescale_factor, spikes_per_second, ring_buffer_sigma,
                 label=None, n_neurons=None, polarity=None):

        # Default to up polarity
        #if polarity is None:
        #    polarity = PushBotRetinaDevice.UP_POLARITY

        self._fixed_key = 0xFEFFF800#(virtual_chip_x << 24 | virtual_chip_y << 16)
        fixed_n_neurons = 32 * 32 * 2 # MERGED
        
        # Lower 13 bits for retina payload
        self._fixed_mask = 0xFFFFF800
        
        #if polarity == PushBotRetinaDevice.UP_POLARITY:
        #    self._fixed_key |= PushBotRetinaDevice.POLARITY_BIT
        #elif polarity == PushBotRetinaDevice.DOWN_POLARITY:
        #   pass
        #else:FFFFF000
        #    assert False

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

        # reset retina
        #reset_command = self.RETINA_RESET
        
        #commands.append(MultiCastCommand(
        #    0, reset_command, self.MANAGEMENT_MASK, 0,
        #    0, 0))
        
        # to ensure populations receive the correct packets, this needs to be
        # different based on which retina
        key_set_payload = 0xFEFFF800#(self._virtual_chip_x << 24 |
                           #self._virtual_chip_y << 16)

        # Set sensor key
        commands.append(MultiCastCommand(
            0, self.SENSOR | self.SENSOR_SET_KEY, self.MANAGEMENT_MASK, key_set_payload,
            0, 0))
        
        # Set pushbot
        commands.append(MultiCastCommand(
            0, self.SENSOR | self.SENSOR_SET_PUSHBOT, self.MANAGEMENT_MASK, 1,
            0, 0))
        
        # Disable retina
        commands.append(MultiCastCommand(
            0, self.RETINA_DISABLE, self.MANAGEMENT_MASK, 0, 
            0, 0))
        
        # Set retina key
        commands.append(MultiCastCommand(
            0, self.RETINA_KEY_SET, self.MANAGEMENT_MASK, key_set_payload,
            0, 0))
        
        # Enable retina
        enable_command = self.RETINA_ENABLE
        commands.append(MultiCastCommand(
            0, enable_command, self.MANAGEMENT_MASK,
            (0 << 29) + (3 << 26),  # **YUCK** mystery flags
            0, 0))

        # disable retina
        commands.append(MultiCastCommand(
            -1, self.RETINA_DISABLE, self.MANAGEMENT_MASK, 0, 
            0, 0))

        return commands

    @property
    def model_name(self):
        return "external retina device at " \
               "with _polarity {}".format(self._polarity)

    def recieves_multicast_commands(self):
        return True

    def is_virtual_vertex(self):
        return True

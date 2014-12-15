from pacman.model.constraints.vertex_requires_multi_cast_source_constraint \
    import VertexRequiresMultiCastSourceConstraint
from spinn_front_end_common.utilities import packet_conversions
from spynnaker_external_devices_plugin.pyNN.abstract_models.\
    abstract_external_retina_device import AbstractExternalRetinaDevice
from pacman.model.constraints.placer_chip_and_core_constraint \
    import PlacerChipAndCoreConstraint
from pacman.model.constraints.key_allocator_routing_constraint import \
    KeyAllocatorRoutingConstraint
from spynnaker.pyNN import exceptions
from spynnaker_external_devices_plugin.pyNN.interfaces.abstract_munich_device\
    import AbstractMunichDevice


class MunichRetinaDevice(AbstractExternalRetinaDevice, AbstractMunichDevice):
    #key codes for the robot retina
    MANAGEMENT_BIT = 0x400
    LEFT_RETINA_ENABLE = 0x45
    RIGHT_RETINA_ENABLE = 0x46
    LEFT_RETINA_DISABLE = 0x45
    RIGHT_RETINA_DISABLE = 0x46
    LEFT_RETINA_KEY_SET = 0x43
    RIGHT_RETINA_KEY_SET = 0x44

    LEFT_RETINA = "LEFT"
    RIGHT_RETINA = "RIGHT"

    def __init__(self, virtual_chip_coords, connected_chip_coords,
                 connected_chip_edge, position, machine_time_step, label=None,
                 n_neurons=None,
                 polarity=AbstractExternalRetinaDevice.MERGED_POLARITY):

        if polarity == MunichRetinaDevice.MERGED_POLARITY:
            n_neurons = 128 * 128 * 2
        else:
            n_neurons = 128 * 128
        AbstractExternalRetinaDevice.__init__(
            self, n_neurons, virtual_chip_coords, connected_chip_coords,
            connected_chip_edge, polarity, machine_time_step=machine_time_step,
            label=label)
        AbstractMunichDevice.__init__(
            self, n_neurons=n_neurons, virtual_chip_coords=virtual_chip_coords,
            connected_node_coords=connected_chip_coords,
            connected_node_edge=connected_chip_edge, label=label,
            machine_time_step=machine_time_step,
            max_atoms_per_core=self._get_max_atoms_per_core(n_neurons))
        self.position = position

        if (self.position != self.RIGHT_RETINA and
           self.position != self.LEFT_RETINA):
            raise exceptions.ConfigurationException(
                "The external Retina does not recognise this position")

        #add commands constraint
        command_constraint = \
            VertexRequiresMultiCastSourceConstraint(self.get_commands())
        self.add_constraint(command_constraint)
        #add routing key constraint
        routing_key_constraint = \
            KeyAllocatorRoutingConstraint(self.generate_routing_info,
                                          self.key_with_neuron_id)
        self.add_constraint(routing_key_constraint)

    def add_constraints_to_subverts(self, subverts):
        ordered_subverts = sorted(subverts, key=lambda x: x.lo_atom)

        start_point = 0
        if self.position == self.RIGHT_RETINA:
            if self.polarity == AbstractExternalRetinaDevice.UP_POLARITY:
                start_point = 8
        elif self.polarity == AbstractExternalRetinaDevice.UP_POLARITY:
            start_point = 24
        else:
            start_point = 16

        for subvert in ordered_subverts:
            constraint = \
                PlacerChipAndCoreConstraint(self._virtual_chip_coords['x'],
                                            self._virtual_chip_coords['y'],
                                            start_point)
            subvert.add_constraint(constraint)
            start_point += 1

    def get_commands(self):
        """
        method that returns the commands for the retina external device
        """
        commands = list()

        #change the retina key it transmits with (based off if its right or left
        if self.position == self.RIGHT_RETINA:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.RIGHT_RETINA_KEY_SET)
        else:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.LEFT_RETINA_KEY_SET)

        #to ensure populations receive the correct packets, this needs to be
        #different bsed on which retina
        if self.position == self.RIGHT_RETINA:
            mgmt_payload = 0 << 24 | 6 << 16
        else:
            mgmt_payload = 0 << 24 | 7 << 16

        command = {'t': 0, "cp": 1, 'key': mgmt_key, 'payload': mgmt_payload,
                   'repeat': 5, 'delay': 1000}
        commands.append(command)

        #make retina enabled (dependant on if its a left or right retina
        if self.position == self.RIGHT_RETINA:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.RIGHT_RETINA_ENABLE)  # enabl
        else:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.LEFT_RETINA_ENABLE)  # enable
        mgmt_payload = 1
        command = {'t': 0, "cp": 1, 'key': mgmt_key, 'payload': mgmt_payload,
                   'repeat': 5, 'delay': 1000}
        commands.append(command)

        # disable retina
        if self.position == self.RIGHT_RETINA:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.RIGHT_RETINA_DISABLE)
        else:
            mgmt_key = (self._virtual_chip_coords['x'] << 24 |
                        self._virtual_chip_coords['y'] << 16 |
                        self.MANAGEMENT_BIT | self.LEFT_RETINA_DISABLE)
        mgmt_payload = 0
        command = {'t': -1, "cp": 1, 'key': mgmt_key,
                   'payload': mgmt_payload, 'repeat': 5, 'delay': 1000}
        commands.append(command)
        return commands

    def key_with_neuron_id(self):
        keys = list()
        key, mask = self.generate_routing_info(None)
        for neuron_id in range(0, self._n_atoms):
            keys.append(key + neuron_id)
        return keys

    def generate_routing_info(self, subedge):
        """
        over loads the generate routing info for virtual key space
        each retina has its own unique outgoing key
        """
        processor_id = subedge.presubvertex.placement.processor.idx % 16
        if self.position == self.RIGHT_RETINA:
            if self.polarity == MunichRetinaDevice.UP_POLARITY:
                part_1 = \
                    packet_conversions.get_key_from_coords(0, 6, processor_id)
                key = part_1 | (1 << 14)
                return key, 0xffff7800
            else:
                key = packet_conversions.get_key_from_coords(0, 6, processor_id)
                return key, 0xffff7800
        else:
            if self.polarity == MunichRetinaDevice.UP_POLARITY:
                key = \
                    packet_conversions.get_key_from_coords(0, 7, processor_id) \
                    | (1 << 14)
                return key, 0xffff7800
            else:
                key = packet_conversions.get_key_from_coords(0, 7, processor_id)
                return key, 0xffff7800

    @property
    def model_name(self):
        return "external retina device at " \
               "position {} and polarity {}".format(self.position,
                                                    self.polarity)

    @staticmethod
    def get_packet_retina_coords(details):
        return (packet_conversions.get_x_from_robot_retina(details),
                packet_conversions.get_y_from_robot_retina(details),
                packet_conversions.get_spike_value_from_robot_retina(details))

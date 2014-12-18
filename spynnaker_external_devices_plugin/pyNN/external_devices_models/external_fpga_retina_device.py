from pacman.model.constraints.key_allocator_routing_constraint import \
    KeyAllocatorRoutingConstraint
from pacman.model.constraints.vertex_requires_multi_cast_source_constraint \
    import VertexRequiresMultiCastSourceConstraint
from spinn_front_end_common.utilities import packet_conversions
from spynnaker_external_devices_plugin.pyNN.interfaces.abstract_FPGA_device \
    import AbstractFPGADevice
from spynnaker_external_devices_plugin.pyNN.abstract_models.\
    abstract_external_retina_device import AbstractExternalRetinaDevice
from spynnaker.pyNN import exceptions


class ExternalFPGARetinaDevice(AbstractExternalRetinaDevice, AbstractFPGADevice):

    MODE_128 = "128"
    MODE_64 = "64"
    MODE_32 = "32"
    MODE_16 = "16"

    def __init__(self, mode, virtual_chip_coords, connected_chip_coords,
                 connected_chip_edge, polarity, machine_time_step, label=None,
                 n_neurons=None):

        if mode == ExternalFPGARetinaDevice.MODE_128:
            if (self.polarity == ExternalFPGARetinaDevice.UP_POLARITY or
               self.polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                n_neurons = 128 * 128
            else:
                n_neurons = 128 * 128 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_64:
            if (self.polarity == ExternalFPGARetinaDevice.UP_POLARITY or
               self.polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                n_neurons = 64 * 64
            else:
                n_neurons = 64 * 64 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_32:
            if (self.polarity == ExternalFPGARetinaDevice.UP_POLARITY or
               self.polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                n_neurons = 32 * 32
            else:
                n_neurons = 32 * 32 * 2
        elif mode == ExternalFPGARetinaDevice.MODE_16:
            if (self.polarity == ExternalFPGARetinaDevice.UP_POLARITY or
               self.polarity == ExternalFPGARetinaDevice.DOWN_POLARITY):
                n_neurons = 16 * 16
            else:
                n_neurons = 16 * 16 * 2
        else:
            raise exceptions.ConfigurationException("the FPGA retina does not "
                                                    "recongise this mode")

        AbstractExternalRetinaDevice.__init__(
            self, n_neurons=n_neurons, virtual_chip_coords=virtual_chip_coords,
            connected_node_coords=connected_chip_coords,
            connected_node_edge=connected_chip_edge,
            machine_time_step=machine_time_step, label=label, polarity=polarity)

        AbstractFPGADevice.__init__(
            self, n_neurons=n_neurons, virtual_chip_coords=virtual_chip_coords,
            connected_node_coords=connected_chip_coords,
            connected_node_edge=connected_chip_edge,
            machine_time_step=machine_time_step, label=label,
            max_atoms_per_core=self._get_max_atoms_per_core(n_neurons))

        #add commands constraint
        command_constraint = \
            VertexRequiresMultiCastSourceConstraint(self.get_commands())
        self.add_constraint(command_constraint)
        #add routing key constraint
        routing_key_constraint = \
            KeyAllocatorRoutingConstraint(self.generate_routing_info,
                                          self.key_with_neuron_id)
        self.add_constraint(routing_key_constraint)

    def get_commands(self):
        """
        method that returns the commands for the retina external device
        """
        commands = list()

        mgmt_key = \
            self._virtual_chip_coords['x'] << 24 | \
            self._virtual_chip_coords['y'] + 1 << 16 | 0xffff

        mgmt_payload = 1
        command = {'t': 0, "cp": 1, 'key': mgmt_key, 'payload': mgmt_payload,
                   'repeat': 5, 'delay': 100}
        commands.append(command)

        mgmt_key = \
            self._virtual_chip_coords['x'] << 24 | \
            self._virtual_chip_coords['y'] + 1 << 16 | 0xfffe
        mgmt_payload = 0
        command = {'t': -1, "cp": 1, 'key': mgmt_key,
                   'payload': mgmt_payload, 'repeat': 5, 'delay': 100}
        commands.append(command)
        return commands

    def key_with_neuron_id(self):
        keys = list()
        key, mask = self.generate_routing_info(None)
        for neuron_id in range(0, self._n_atoms):
            keys.append(key + neuron_id)
        return keys

    # noinspection PyUnusedLocal
    def generate_routing_info(self, subedge):
        """
        over writes component method, return the key and mask
        """
        if self.polarity is None:
            key = \
                self._virtual_chip_coords['x'] << 24 | \
                self._virtual_chip_coords['y'] << 16
            mask = 0xffff0000
            return key, mask
        elif self.polarity == ExternalFPGARetinaDevice.UP_POLARITY:
            key = \
                self._virtual_chip_coords['x'] << 24 | \
                self._virtual_chip_coords['y'] << 16 | \
                1 << 14
            mask = 0xffffC000
            return key, mask
        elif self.polarity == ExternalFPGARetinaDevice.DOWN_POLARITY:
            key = \
                self._virtual_chip_coords['x'] << 24 | \
                self._virtual_chip_coords['y'] << 16
            mask = 0xffffC000
            return key, mask
        else:
            raise exceptions.ConfigurationException(
                "The FPGA retina requires the poloarity parameter to either be "
                "UP, DOWN or None. Other values result in the Model not "
                "knowing how to initlise its key and mask.")

    @property
    def model_name(self):
        """
        name for debugs
        """
        return "external FPGA retina device"

    @staticmethod
    def get_packet_retina_coords(details, mode):
        return packet_conversions.get_x_from_fpga_retina(details, mode), \
            packet_conversions.get_y_from_fpga_retina(details, mode), \
            packet_conversions.get_spike_value_from_fpga_retina(details,
                                                                mode)

    def is_external_retina(self):
        return True
#pacman imports
from pacman.model.constraints.\
    vertex_requires_virtual_chip_in_machine_constraint import \
    VertexRequiresVirtualChipInMachineConstraint

#spinnmachine imports
from spinn_machine.abstract_virtual_vertex \
    import AbstractVirtualVertex

#inhittance imports
from abc import ABCMeta
from six import add_metaclass
from abc import abstractmethod


@add_metaclass(ABCMeta)
class AbstractExternalDevice(AbstractVirtualVertex):
    def __init__(self, n_neurons, virtual_chip_coords, connected_node_coords,
                 connected_node_edge, machine_time_step, label,
                 max_atoms_per_core):
        AbstractVirtualVertex.__init__(
            self, n_neurons, virtual_chip_coords, connected_node_coords,
            connected_node_edge, machine_time_step, label, max_atoms_per_core)
        vertex_virtual_chip_constraint = \
            VertexRequiresVirtualChipInMachineConstraint(
                virtual_chip_coords, connected_node_coords, connected_node_edge)
        self.add_constraint(vertex_virtual_chip_constraint)

    @property
    def model_name(self):
        return "ExternalDevice:{}".format(self.label)

    @abstractmethod
    def is_external_device(self):
        """ helper method for is instance

        :return:
        """


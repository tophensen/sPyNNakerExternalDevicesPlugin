from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex

from spynnaker.pyNN.models.abstract_models.abstract_vertex_with_dependent_vertices \
    import AbstractVertexWithEdgeToDependentVertices
from pacman.model.constraints.key_allocator_constraints.key_allocator_fixed_key_and_mask_constraint \
    import KeyAllocatorFixedKeyAndMaskConstraint
from pacman.model.routing_info.base_key_and_mask import BaseKeyAndMask

from spinn_front_end_common.abstract_models.abstract_provides_outgoing_edge_constraints\
    import AbstractProvidesOutgoingEdgeConstraints

class MunichIODeviceSource(AbstractVirtualVertex, AbstractProvidesOutgoingEdgeConstraints):

    def __init__(self, spinnaker_link_id, msg_key, msg_mask=0xFFFFFFFF):

        self.key = msg_key
        self.mask = msg_mask
        
        AbstractVirtualVertex.__init__(
            self, 1, spinnaker_link_id, "External IO Device",
            max_atoms_per_core=1)
            
        AbstractProvidesOutgoingEdgeConstraints.__init__(self)
#        AbstractVertexWithEdgeToDependentVertices.__init__(
#            self, dependent_vertices)

    @property
    def model_name(self):
        return "external io device"

    def is_virtual_vertex(self):
        return True
        
#    def has_dependent_vertices(self):
#        return True

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
    # Any key to the device will work, as long as it doesn't set the
    # management bit. We also need enough for the configuration bits
    # and the management bit anyway
        return list([KeyAllocatorFixedKeyAndMaskConstraint([BaseKeyAndMask(self.key, self.mask)])])
        

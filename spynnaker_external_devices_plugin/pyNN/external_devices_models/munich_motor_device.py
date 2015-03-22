from spynnaker.pyNN.models.abstract_models.abstract_virtual_vertex \
    import AbstractVirtualVertex


class MunichMotorDevice(AbstractVirtualVertex):

    def __init__(self, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_to_real_chip_link_id):

        AbstractVirtualVertex.__init__(
            self, 6, virtual_chip_x, virtual_chip_y,
            connected_to_real_chip_x, connected_to_real_chip_y,
            connected_to_real_chip_link_id, "External Munich Motor",
            max_atoms_per_core=6)

    @property
    def model_name(self):
        return "external motor device"

    def is_virtual_vertex(self):
        return True

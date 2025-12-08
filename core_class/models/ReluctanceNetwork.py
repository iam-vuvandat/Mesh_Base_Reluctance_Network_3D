
from core_class.utils.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from core_class.utils.create_elements import create_elements
from core_class.utils.show_reluctance_network import show_reluctance_network

class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None):
        self.material_database = motor.material_database
        self.geometry = geometry
        self.mesh = mesh

        find_geometry_dimension_in_mesh(geometry= geometry,
                                        mesh= mesh)
        self.elements = create_elements(self)

    def show(self):
        show_reluctance_network(reluctance_network=self)
    

from core_class.utils.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from core_class.utils.create_elements import create_elements

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

    
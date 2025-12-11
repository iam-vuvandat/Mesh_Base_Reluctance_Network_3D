
from core_class.utils.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from core_class.utils.create_elements import create_elements
from core_class.utils.show_reluctance_network import show_reluctance_network
from core_class.utils.create_magnetic_potential import create_magnetic_potential
from core_class.utils.create_winding_current import create_winding_current

class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None,
                 magnetic_potential = None,
                 winding_current = None):
        self.material_database = motor.material_database
        self.geometry = geometry
        self.mesh = mesh
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current
        find_geometry_dimension_in_mesh(geometry= geometry,
                                        mesh= mesh)
        
        self.winding_current = create_winding_current(reluctance_network=self)
        self.magnetic_potential = create_magnetic_potential(reluctance_network= self)
        self.elements = create_elements(self)








































    def show(self):
        show_reluctance_network(reluctance_network=self)
    
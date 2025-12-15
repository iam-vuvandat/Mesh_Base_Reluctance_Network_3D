from core_class.utils.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from core_class.utils.create_elements import create_elements
from core_class.utils.show_reluctance_network import show_reluctance_network
from core_class.utils.create_magnetic_potential import create_magnetic_potential
from core_class.utils.create_winding_current import create_winding_current
from core_class.utils.update_reluctance_network import update_reluctance_network
from core_class.utils.set_minimum_reluctance import set_minimum_reluctance
from solver.core.create_magnetic_potential_equation import create_magnetic_potential_equation
from solver.core.solve_magnetic_equation import solve_magnetic_equation

class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None,
                 magnetic_potential = None,
                 winding_current = None,):
        
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
    
    def update_reluctance_network(self,
                                  magnetic_potential = None,
                                  winding_current = None):
        
        update_reluctance_network(reluctance_network=self,
                                  magnetic_potential = magnetic_potential,
                                  winding_current = winding_current)

    def set_minimum_reluctance(self):
        set_minimum_reluctance(reluctance_network=self)

    def create_magnetic_potential_equation(self,
                                           use_minimum_reluctance = False):
        return create_magnetic_potential_equation(reluctance_network= self,
                                                  use_minimum_reluctance= use_minimum_reluctance)

    def solve_magnetic_equation(self,
                                max_iteration =1,
                                max_relative_residual = 0.00001,
                                damping_factor = 0.00005,
                                debug = True):
        solve_magnetic_equation(reluctance_network = self,
                                max_iteration = max_iteration,
                                max_relative_residual = max_relative_residual,
                                damping_factor = damping_factor,
                                debug = debug)



































    def show(self):
        show_reluctance_network(reluctance_network=self)
    
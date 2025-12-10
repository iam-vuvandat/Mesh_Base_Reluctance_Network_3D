from core_class.utils.extract_element_info import extract_element_info

class Element:
    def __init__(self,
                 motor = None,
                 position = None,
                 geometry = None,
                 mesh = None,
                 magnetic_potential = None,
                 winding_current = None):
        self.position = position
        self.material_database = motor.material_database
        self.position = position
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current

        info = extract_element_info(position=position,
                                    geometry=geometry,
                                    mesh=mesh,
                                    )
        # material
        self.material = info.material

        # dimension
        self.dimension = info.dimension

        # coordinate
        self.coordinate = info.coordinate

        # magnet properties
        self.segment_magnet_source = info.magnet_source
        self.magnetization_direction = info.magnetization_direction

        # winding properties
        self.segment_winding_vector = info.winding_vector
        self.winding_normal = info.winding_normal

        # pre - define

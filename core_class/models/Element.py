from core_class.utils.extract_element_info import extract_element_info

class Element:
    def __init__(self,
                 motor = None,
                 position = None,
                 geometry = None,
                 mesh = None,
                 loop_flux = None,
                 winding_current = None):
        self.position = position
        self.material_database = motor.material_database
        self.position = position
        self.loop_flux = loop_flux
        self.winding_current = winding_current

        info = extract_element_info(position=position,
                                    geometry=geometry,
                                    mesh=mesh,
                                    )
        # material
        self.material = info.material

        # segment dimension
        self.segment_r_length = info.segment_r_length
        self.segment_t_length = info.segment_t_length
        self.segment_t_length = info.segment_t_length

        # element dimension
        self.element_r_length = info.element_r_length
        self.element_t_length = info.element_t_length
        self.element_z_length = info.element_z_length

        # magnet properties
        self.segment_magnet_source = info.magnet_source
        self.magnetization_direction = info.magnetization_direction

        # winding properties
        self.segment_winding_vector = info.winding_vector
        self.winding_normal = info.winding_normal
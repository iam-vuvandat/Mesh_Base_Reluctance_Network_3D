from core_class.utils.extract_element_info import extract_element_info

class Element:
    def __init__(self,
                 motor = None,
                 position = None,
                 geometry = None,
                 mesh = None,
                 loop_flux = None,
                 winding_current = None):
        
        self.material_database = motor.material_database
        self.position = position
        self.loop_flux = loop_flux
        self.winding_current = winding_current

        info = extract_element_info(position=position,
                                    geometry=geometry,
                                    mesh=mesh,
                                    )
        
        self.material = info.material
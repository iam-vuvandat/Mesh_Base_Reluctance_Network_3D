class Element:
    def __init__(self,motor,
                 position,
                 geometry,
                 mesh,
                 loop_flux,
                 winding_current):
        
        self.material_database = motor.material_database
        self.position = position
        self.loop_flux = loop_flux
        self.winding_current = winding_current

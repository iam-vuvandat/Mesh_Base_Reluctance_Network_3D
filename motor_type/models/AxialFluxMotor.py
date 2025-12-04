# Init Axial Flux Motor : single stator, single rotor, parallel slot, surface mount magnet, surface radial
class AxialFluxMotor_type1:
    def __init__(self,
                 # radial_stator_parameter
                 slot_number = 15,
                 stator_lam_dia = 150 * 1e-3,
                 stator_bore_dia = 50 * 1e-3,
                 slot_opening = 5 * 1e-3,
                 wdg_extension_inner = 0,
                 wdg_extension_outer = 0,
                 # radial_rotor_parameter
                 pole_number = 10,
                 rotor_lam_dia = 150 * 1e-3,
                 magnet_embed_depth = 5* 1e-3, 
                 rotor_web_thickness = 5 * 1e-3, 
                 magnet_depth = 40 * 1e-3 ,
                 magnet_segments = 1 ,
                 banding_depth = 0 * 1e-3,
                 shaft_dia = 0 * 1e-3,
                 shaft_hole_diameter = 50 * 1e-3,
                 # linear_stator_parameter 
                 slot_width = 7 * 1e-3,
                 slot_depth = 20 * 1e-3,
                 slot_corner_radius = 0, #deg
                 tooth_tip_depth = 2 * 1e-3,
                 tooth_tip_angle = 30, # deg
                 stator_length = 30* 1e-3,
                 # linear_rotor_parameter 
                 airgap = 2 * 1e-3,
                 magnet_length = 2, 
                 rotor_length = 10,
                 # winding  
                 ):
        pass
from motor_type.utils.for_axial_flux_motor_type_1.find_symmetry_factor import find_symmetry_factor
from motor_type.utils.for_axial_flux_motor_type_1.find_winding_matrix import find_winding_matrix

# Init Axial Flux Motor : single stator, single rotor, parallel slot, surface mount magnet, surface radial
class AxialFluxMotorType1:
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
                 magnet_embed_depth = 5 * 1e-3, 
                 rotor_web_thickness = 5 * 1e-3, 
                 magnet_depth = 40 * 1e-3,
                 magnet_segments = 1,
                 banding_depth = 0 * 1e-3,
                 shaft_dia = 0 * 1e-3,
                 shaft_hole_diameter = 50 * 1e-3,
                 # linear_stator_parameter 
                 slot_width = 7 * 1e-3,
                 slot_depth = 20 * 1e-3,
                 slot_corner_radius = 0, # deg
                 tooth_tip_depth = 2 * 1e-3,
                 tooth_tip_angle = 30, # deg
                 stator_length = 30 * 1e-3,
                 # linear_rotor_parameter 
                 airgap = 2 * 1e-3,
                 magnet_length = 2 * 1e-3,    
                 rotor_length = 10 * 1e-3,    
                 # winding  
                 phase = 3,
                 turns = 50,
                 throw = 1,
                 parallel_path = 1,
                 winding_layer = 2,
                 winding_type = "concentrated",
                 winding_matrix = None,
                 ):
        
        # --- Gán Radial Stator Parameters ---
        self.slot_number = slot_number
        self.stator_lam_dia = stator_lam_dia
        self.stator_bore_dia = stator_bore_dia
        self.slot_opening = slot_opening
        self.wdg_extension_inner = wdg_extension_inner
        self.wdg_extension_outer = wdg_extension_outer

        # --- Gán Radial Rotor Parameters ---
        self.pole_number = pole_number
        self.rotor_lam_dia = rotor_lam_dia
        self.magnet_embed_depth = magnet_embed_depth
        self.rotor_web_thickness = rotor_web_thickness
        self.magnet_depth = magnet_depth
        self.magnet_segments = magnet_segments
        self.banding_depth = banding_depth
        self.shaft_dia = shaft_dia
        self.shaft_hole_diameter = shaft_hole_diameter

        # --- Gán Linear Stator Parameters ---
        self.slot_width = slot_width
        self.slot_depth = slot_depth
        self.slot_corner_radius = slot_corner_radius
        self.tooth_tip_depth = tooth_tip_depth
        self.tooth_tip_angle = tooth_tip_angle
        self.stator_length = stator_length

        # --- Gán Linear Rotor Parameters ---
        self.airgap = airgap
        self.magnet_length = magnet_length
        self.rotor_length = rotor_length

        # --- Gán Winding Parameters ---
        self.phase = phase
        self.turns = turns
        self.throw = throw
        self.parallel_path = parallel_path
        self.winding_layer = winding_layer
        self.winding_type = winding_type
        self.winding_matrix = winding_matrix

        
        symmetry_data = find_symmetry_factor(self)
        self.symmetry_factor = symmetry_data.symmetry_factor

        winding_data = find_winding_matrix(self)
        self.winding_matrix = winding_data.winding_matrix
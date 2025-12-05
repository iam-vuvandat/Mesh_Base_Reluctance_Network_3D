import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
import math 
pi = math.pi

from motor_type.utils.for_create_geometry.create_cylinder import create_cylinder
from motor_type.utils.for_create_geometry.create_tube import create_tube
from motor_type.utils.for_create_geometry.create_cylindrical_shell_segment import create_cylindrical_shell_segment
from core_class.models.Segment import Segment
from core_class.models.Geometry import Geometry



def create_geometry(motor,
                    rotor_angle_offset = 0, #rad
                    stator_angle_offset = 0): #rad
    
    geometry = []
    # create_rotor_yoke
    rotor_yoke_mesh = create_tube(inner_radius=motor.shaft_hole_diameter/2,
                                  outer_radius=motor.rotor_lam_dia/2,
                                  height = motor.rotor_length,
                                )
    rotor_yoke_template = Segment(mesh= rotor_yoke_mesh,
                                  material = "iron",
                                  magnet_source= 0.0,
                                  )
    geometry.append(rotor_yoke_template)

    #create_magnet
    pole_number = motor.pole_number
    pole_arc = 2*pi / pole_number
    magnet_open_arc = pole_arc * motor.magnet_arc /180
    magnet_z_offset = motor.rotor_length
    magnet_height = motor.magnet_length
    magnet_coercivity = motor.material_database.magnet.coercivity
    magnet_source = magnet_coercivity * magnet_height
    magnet_outer_radius = motor.rotor_lam_dia/2 - motor.magnet_embed_depth
    magnet_inner_radius = magnet_outer_radius - motor.magnet_depth

    for i in range(int(pole_number)):
        magnet_mesh = create_cylindrical_shell_segment(inner_radius=magnet_inner_radius,
                                                         outer_radius= magnet_outer_radius,
                                                         height = magnet_height,
                                                         angle_rad= magnet_open_arc,
                                                         center_angle_rad= rotor_angle_offset + i*pole_arc,
                                                         z_offset= magnet_z_offset,
                                                         )
        sign = None
        if i%2 == 0:
            sign = 1
        else:
            sign = -1

        magnet_template = Segment(mesh = magnet_mesh,
                                  material= "magnet",
                                  magnet_source= magnet_source,
                                  magnetization_direction=np.array([0,0,sign]))
        geometry.append(magnet_template)
    
    # Create tooth tip
    slot_arc = 2*pi / motor.slot_number
    

    return Geometry(geometry=geometry)

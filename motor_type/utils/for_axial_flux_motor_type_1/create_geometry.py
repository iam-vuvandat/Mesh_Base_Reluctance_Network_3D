import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
import math 
pi = math.pi

from motor_type.utils.for_create_geometry import create_cylinder
from core_class.models.Segment import Segment


def create_geometry(motor,
                    rotor_angle_offset = 0, #rad
                    stator_angle_offset = 0): #rad
    
    rotor_yoke = create_cylinder
    # create_rotor_yoke
    return []
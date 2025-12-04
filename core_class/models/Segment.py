import numpy as np 
import math 
pi = math.pi

class Segment:
    def __init__(self,
                 mesh = None,
                 material = "air",
                 magnet_source = 0.0,
                 magnetization_direction = np.array([0,0,1]),
                 winding_vector = np.array([0,0,0]),
                 winding_normal = np.array([0,0,1]),
                 angular_length = 0.0,
                 radial_length = 0.0,
                 axial_length = 0.0):
        
        self.mesh = mesh
        self.material = material
        self.magnet_source = magnet_source
        self.magnetization_direction = magnetization_direction
        self.winding_vector = winding_vector
        self.winding_normal = winding_normal
        self.angular_length = angular_length
        self.radial_length = radial_length
        self.axial_length = axial_length
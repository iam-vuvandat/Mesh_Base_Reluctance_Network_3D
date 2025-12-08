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
                 r_length = None,
                 t_length = None,
                 z_length = None):
        
        self.mesh = mesh
        self.material = material
        self.magnet_source = magnet_source
        self.magnetization_direction = magnetization_direction
        self.winding_vector = winding_vector
        self.winding_normal = winding_normal

        self.r_length = r_length
        self.t_length = t_length
        self.z_length = z_length
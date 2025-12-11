from dataclasses import dataclass
import numpy as np

@dataclass
class Output:
    magnet_source: np.ndarray

def find_magnet_source(element):
    dims = element.dimension
    
    if np.any(dims == 0):
        return Output(magnet_source=np.zeros((2, 3)))

    mag = float(element.segment_magnet_source)
    u = element.magnetization_direction

    f_seg = np.array([
        mag * u[0] * np.cos(u[1]), 
        mag * u[0] * np.sin(u[1]), 
        mag * u[2]
    ])

    ratio = dims[0] / dims[1]
    f_half = (f_seg * ratio) * 0.5
    
    return Output(magnet_source=np.array([f_half, f_half]))


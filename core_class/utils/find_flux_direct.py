from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    flux_direct : Any

def find_flux_direct(element):
    magnetic_potential = element.magnetic_potential
    i,j,k = element.position
    flux_direct = np.zeros((2,3))
    neighbor_elements = element.neighbor_elements()
    
    


    return Output(flux_direct= flux_direct)

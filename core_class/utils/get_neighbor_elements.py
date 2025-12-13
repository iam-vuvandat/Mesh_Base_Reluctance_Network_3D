from dataclasses import dataclass
import numpy as np
from typing import Any, Tuple

from shapely import boundary

@dataclass
class Output:
    neighbor_elements: Any

def get_neighbor_elements(element):
    elements_list = element.elements
    neighbor_elements = np.empty((2,3),dtype= object)
    i,j,k = element.position
    nr,nt,nz = element.magnetic_potential.data.shape
    periodic_boundary = element.periodic_boundary

    if i-1 >= 0 and i-1 < nr : 
        neighbor_elements[0,0] = elements_list[i-1,j,k]
    else:
        neighbor_elements[0,0] = None
    
    if i+1 >= 0 and i +1 < nr : 
        neighbor_elements[1,0] = elements_list[i+1,j,k]
    else:
        neighbor_elements[1,0] = None

    if periodic_boundary == False:
        if j-1 >= 0 and j -1 < nt : 
            neighbor_elements[0,1] =elements_list[i,j-1,k]
        else:
            neighbor_elements[0,1] = None

        if j+1 >= 0 and j +1 < nt : 
            neighbor_elements[1,1] =elements_list[i,j+1,k]
        else:
            neighbor_elements[1,1] = None
    else:
        neighbor_elements[0,1] = elements_list[i,(j-1)% nt,k]
        neighbor_elements[1,1] = elements_list[i,(j+1)% nt,k]

    if k-1 >= 0 and k-1 < nz : 
        neighbor_elements[0,2] = elements_list[i,j,k-1]
    else:
        neighbor_elements[0,2] = None

    if k+1 >= 0 and k+1 < nz : 
        neighbor_elements[1,2] = elements_list[i,j,k+1]
    else:
        neighbor_elements[1,2] = None
    

    return Output(neighbor_elements= neighbor_elements)
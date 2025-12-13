#import paths
from dataclasses import dataclass
import numpy as np
from typing import Any, Tuple

@dataclass
class Output:
    value: float
    valid: bool
    index : float

@dataclass
class Output2:
    three_dimension_index: Tuple[int, int, int]

class MagneticPotential:
    def __init__(self, data=None, periodic_boundary=True):
        self.data = data
        self.periodic_boundary = periodic_boundary

    def retrieve(self, position):
        i, j, k = position
        nr, nt, nz = self.data.shape

        if not (0 <= i < nr and 0 <= k < nz):
            return Output(value=0.0, valid=False , index= -1)

        if self.periodic_boundary:
            j = j % nt
        elif not (0 <= j < nt):
            return Output(value=0.0, valid=False, index= -1)

        value = self.data[i, j, k]
        flat_index = k * nz + j * nt + i * nr
        return Output(value=value.item(), valid=True, index= flat_index)
    
    def get_3D_index(self, position):
        nr, nt, nz = self.data.shape
        i = position % nr    
        position = position // nr
        j = position % nt  
        k = position // nt 
        return Output2(three_dimension_index=(i, j, k))

if __name__ == "__main__":
    data = np.array(np.random.random((2, 3, 4)), order='F')
    magnetic_potential = MagneticPotential(data=data,
                                           periodic_boundary= True)
    data1= magnetic_potential.retrieve((0,0,5))
    print(data)
    print(data1)

    print(magnetic_potential.get_3D_index(15).three_dimension_index)
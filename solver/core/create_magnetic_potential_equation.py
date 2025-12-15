from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any
    J: Any

def create_magnetic_potential_equation(reluctance_network,
                                       use_minimum_reluctance=False,
                                       debug=True):
    if use_minimum_reluctance:
        reluctance_network.set_minimum_reluctance()

    mesh = reluctance_network.mesh
    matrix_size = mesh.total_cells - 1
    magnetic_potential = reluctance_network.magnetic_potential
    G = [[], [], []]
    J = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Creating Matrix Equation")

    for i_th in iterator:
        elements = reluctance_network.elements
        i, j_coord, k = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[i, j_coord, k]
        
        neighbor_elements = element_center.neighbor_elements()
        
        j_val = 0.0
        U_center_factor = 0.0

        for m in [0, 1]:
            if m == 0:
                sign = [1, 0]
            else:
                sign = [0, 1]
            
            for n in [0, 1, 2]:
                if neighbor_elements[m, n] is not None:
                    element_nei = neighbor_elements[sign[1], n]
                    
                    f = element_nei.magnetic_source[sign[0], n] + element_center.magnetic_source[sign[1], n]
                    r = (element_nei.reluctance[sign[0], n] + element_center.reluctance[sign[1], n])

                    j_val = j_val - (f / r)
                    
                    if element_nei.flat_position < matrix_size:
                        G[0].append(i_th)
                        G[1].append(element_nei.flat_position)
                        G[2].append(1 / r)

                    U_center_factor = U_center_factor - (1 / r)

        G[0].append(i_th)
        G[1].append(i_th)
        G[2].append(U_center_factor)
        J[i_th] = j_val

    G = sp.csr_matrix((G[2], (G[0], G[1])), shape=(matrix_size, matrix_size))

    return Output(G=G, J=J)
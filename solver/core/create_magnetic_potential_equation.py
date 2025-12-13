import numpy as np
import scipy.sparse as sp


def create_magnetic_potential_equation(reluctance_network,
                                       use_minimum_reluctance = False):
    # Phương trình có dạng G * U = J 
    matrix_size = reluctance_network.mesh.total_cells -1 # nút cuối cùng tham chiếu = 0
    G = [[],[],[]]
    J = np.zeros(matrix_size)
    
    for i in range(matrix_size):
        





        1
    return 1


import numpy as np
from scipy.sparse.linalg import spsolve
from tqdm import tqdm

def solve_magnetic_equation(reluctance_network,
                            max_iteration=20,
                            max_relative_residual=0.01,
                            damping_factor=0.1,
                            debug=True):
    
    current_relative_residual = max_relative_residual + 1.0
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape

    iterator = range(max_iteration)
    if debug:
        iterator = tqdm(iterator, desc="Solving Magnetic Equation")

    for i in iterator:
        if i == 0:
            current_damping_factor = 1.0
            equation_component = reluctance_network.create_magnetic_potential_equation(use_minimum_reluctance=True)
        else:
            current_damping_factor = damping_factor
            equation_component = reluctance_network.create_magnetic_potential_equation(use_minimum_reluctance=False)
        
        G = equation_component.G
        J = equation_component.J

        solved_vector = spsolve(G, J)
        solved_vector_with_ref = np.append(solved_vector, 0.0)
        magnetic_potential_solved = solved_vector_with_ref.reshape(magnetic_potential_shape, order='F')

        current_magnetic_potential = reluctance_network.magnetic_potential.data

        delta = np.linalg.norm(magnetic_potential_solved - current_magnetic_potential)
        current_relative_residual = delta / (np.linalg.norm(current_magnetic_potential) + 1e-12)

        if debug:
            iterator.set_postfix(residual=f"{current_relative_residual:.6e}")

        if i > 0 and current_relative_residual < max_relative_residual:
            reluctance_network.magnetic_potential.data = magnetic_potential_solved
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            break

        next_magnetic_potential = current_magnetic_potential * (1 - current_damping_factor) + magnetic_potential_solved * current_damping_factor
        
        reluctance_network.magnetic_potential.data = next_magnetic_potential
        reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
    return reluctance_network
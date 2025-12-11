def update_reluctance_network(reluctance_network, 
                              magnetic_potential = None,
                              winding_current = None):
    
    reluctance_network.magnetic_potential = magnetic_potential
    reluctance_network.winding_current = winding_current

    for element in reluctance_network.elements.flat:
        element.update_element(magnetic_potential = magnetic_potential,
                               winding_current = winding_current)
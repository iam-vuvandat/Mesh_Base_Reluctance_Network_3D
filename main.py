from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace



re_create_motor = True

if re_create_motor == False:
    aft = workspace.load("aft1")
else:
    workspace.clear()
    aft = AxialFluxMotorType1()
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)
    workspace.save(aft1 = aft)

aft.show()
aft.reluctance_network.solve_magnetic_equation()
# save motor solved
workspace.save(aft2 = aft)
aft.reluctance_network.show()




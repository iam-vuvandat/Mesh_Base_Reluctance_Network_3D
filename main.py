#from system.core.install_library import install_library
from matplotlib.pylab import False_
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace

re_create_motor = False

if re_create_motor == False:
    aft = workspace.load("aft1")
else:
    aft = AxialFluxMotorType1()
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    workspace.save(aft1 = aft)

aft.show()
aft.reluctance_network.show()
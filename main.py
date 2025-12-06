from system.core.install_library import install_library

from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
aft = AxialFluxMotorType1()
aft.create_geometry(create_rotor_yoke = True,
                    create_stator_yoke = True,
                    create_tooth = True)
aft.geometry.show()
aft.create_adaptive_mesh()
aft.mesh.show()
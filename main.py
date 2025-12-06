from system.core.install_library import install_library

from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
aft = AxialFluxMotorType1()
aft.create_geometry(create_rotor_yoke = False,
                    create_stator_yoke = False,
                    create_tooth = True)
aft.geometry.show()


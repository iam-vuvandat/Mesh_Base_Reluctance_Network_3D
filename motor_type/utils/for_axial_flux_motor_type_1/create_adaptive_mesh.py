from core_class.models.CylindricalMesh import CylindricalMesh
import numpy as np
import math
pi = math.pi

def create_adaptive_mesh(motor,
                         n_r_in=3,
                         n_r_1=4,
                         n_r_2=4,
                         n_r_3=4,
                         n_r_out=3,
                         n_theta=180,
                         n_z_in_air=3,
                         n_z_rotor_yoke=4,
                         n_z_magnet=4,
                         n_z_airgap=5,
                         n_z_tooth_tip_1=1,
                         n_z_tooth_tip_2=4,
                         n_z_tooth_body=4,
                         n_z_stator_yoke=3,
                         n_z_out_air=3,
                         use_symmetry_factor=True,
                         periodic_boundary=True):
    

    # --- Xử lý Radial (R) ---
    # Logic cũ của bạn ok, nhưng hơi rườm rà. Giữ nguyên logic nhưng viết gọn:
    r_min = motor.shaft_hole_diameter/2 if motor.stator_bore_dia > motor.shaft_hole_diameter else motor.stator_bore_dia/2
    
    # r_max biến này tính ra nhưng không thấy dùng? (Có thể xóa nếu không cần)
    r_max = motor.stator_lam_dia/2 if motor.stator_lam_dia > motor.rotor_lam_dia else motor.rotor_lam_dia/2

    r_in = np.linspace(r_min * 0.9, motor.shaft_hole_diameter / 2, n_r_in)

    r_1 = np.linspace(r_in[-1],
                      r_in[-1] + motor.rotor_lam_dia / 2 - motor.magnet_embed_depth - motor.magnet_depth- motor.shaft_hole_diameter / 2,
                      n_r_1)
    r_2 = np.linspace(r_1[-1],
                      r_1[-1] + motor.magnet_depth,
                      n_r_2)
    r_3 = np.linspace(r_2[-1],
                      r_2[-1] + motor.magnet_embed_depth,
                      n_r_3)
    r_out = np.linspace(r_3[-1],
                        r_3[-1] * 1.1,
                        n_r_out)

    r_cordinate = np.concatenate([r_in,
                                  r_1[1:],
                                  r_2[1:],
                                  r_3[1:],
                                  r_out[1:]])

    if use_symmetry_factor == True: 
        symmetry_factor = motor.symmetry_factor
        theta_min = 0 
        theta_max = 2*pi / symmetry_factor
        theta_cordinate = np.linspace(theta_min,theta_max,n_theta)
    else:
        theta_cordinate = np.linspace(0,2*pi,n_theta)

    z_air_in = np.linspace(-motor.rotor_length,
                           0,
                           n_z_in_air)
    z_rotor_yoke_cordinate = np.linspace(0,
                                         motor.rotor_length,
                                         n_z_rotor_yoke)
    z_magnet_cordinate = np.linspace(z_rotor_yoke_cordinate[-1],
                                     z_rotor_yoke_cordinate[-1]+ motor.magnet_length,
                                     n_z_magnet)
    z_airgap_cordinate = np.linspace(z_magnet_cordinate[-1],
                                     z_magnet_cordinate[-1] + motor.airgap,
                                     n_z_airgap)
    z_tooth_tip_1_cordinate = np.linspace(z_airgap_cordinate[-1],
                                          z_airgap_cordinate[-1]+ motor.tooth_tip_depth,
                                          n_z_tooth_tip_1)
    C_in = motor.stator_bore_dia * pi
    C_in_per_slot = C_in / motor.slot_number
    w1 = (1/2) * (motor.slot_width - motor.slot_opening)
    h1 = w1 * np.tan(np.radians(motor.tooth_tip_angle))
    z_tooth_tip_2_cordinate = np.linspace(z_tooth_tip_1_cordinate[-1],
                                          z_tooth_tip_1_cordinate[-1] + h1,
                                          n_z_tooth_tip_2)
    
    # dòng này đúng, lấy z_tooth_tip_1_cordinate[-1] là đúng
    z_tooth_cordinate = np.linspace(z_tooth_tip_1_cordinate[-1],
                                    z_tooth_tip_1_cordinate[-1]+ motor.slot_depth,
                                    n_z_tooth_body)
    
    z_stator_yoke_cordinate = np.linspace(z_tooth_cordinate[-1],
                                          z_tooth_cordinate[-1]+ motor.stator_length - motor.tooth_tip_depth - motor.slot_depth,
                                          n_z_stator_yoke)
    z_air_out = np.linspace(z_stator_yoke_cordinate[-1],
                            z_stator_yoke_cordinate[-1] +motor.stator_length - motor.tooth_tip_depth - motor.slot_depth,
                             n_z_out_air )

    z_cordinate = np.concatenate([z_air_in,
                                  z_rotor_yoke_cordinate[1:],
                                  z_magnet_cordinate[1:],
                                  z_airgap_cordinate[1:],
                                  z_tooth_tip_1_cordinate[1:],
                                  z_tooth_tip_2_cordinate[1:],
                                  z_tooth_cordinate[1:],
                                  z_stator_yoke_cordinate[1:],
                                  z_air_out[1:]
                                  ])
    
    return CylindricalMesh(r_nodes=r_cordinate,
                           theta_nodes= theta_cordinate,
                           z_nodes=z_cordinate,
                           periodic_boundary= periodic_boundary)
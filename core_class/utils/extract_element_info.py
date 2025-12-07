from dataclasses import dataclass, field
import numpy as np
from typing import Optional

@dataclass
class ElementInfo:
    """
    Chứa thông tin phần tử lưới, khớp với cấu trúc class Segment mới.
    """
    # --- Nhóm 1: Định danh ---
    material: str = "air"
    index: int = 0  # Segment hiện tại không có index, nhưng có thể gán bên ngoài nếu cần
    
    # --- Nhóm 2: Từ tính (Magnet Properties) ---
    magnet_source: float = 0.0
    # Vector hướng từ hóa (3D)
    magnetization_direction: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    
    # --- Nhóm 3: Dây quấn (Winding Properties) ---
    # Vector hướng dây quấn (3D)
    winding_vector: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    # Vector pháp tuyến mặt cắt dây (3D)
    winding_normal: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    
    # --- Nhóm 4: Kích thước Grid (Tính từ lưới r, theta, z) ---
    # Dùng để tính toán thể tích phần tử (Integration Volume)
    axial_length: float = 0.0           # d_z
    inner_radius: float = 0.0           # r_i
    outer_radius: float = 0.0           # r_i+1
    arc_length: float = 0.0             # r_avg * d_theta
    opening_angle: float = 0.0          # d_theta
    radial_thickness: float = 0.0       # d_r
    
    # --- Nhóm 5: Kích thước kế thừa từ Segment (Inherited Geometry) ---
    # Nếu Segment có kích thước riêng, dùng nó. Nếu không (None), fallback về kích thước Grid.
    segment_angular_length: float = 0.0
    segment_radial_length: float = 0.0
    segment_axial_length: float = 0.0

    def __repr__(self):
        return (f"Element(mat='{self.material}', "
                f"mag={self.magnet_source:.2f}, "
                f"wind_vec={self.winding_vector})")
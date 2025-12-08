from dataclasses import dataclass, field
import numpy as np
import trimesh
from collections import defaultdict
from typing import Optional, List, Any

@dataclass
class ElementInfo:
    """
    Chứa thông tin phần tử lưới (Voxel) sau khi trích xuất.
    """
    # --- Định danh & Vật liệu ---
    material: str = "air"
    
    # --- Từ tính & Dây quấn ---
    magnet_source: float = 0.0
    magnetization_direction: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))
    winding_vector: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    winding_normal: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))

    # --- Kích thước lưới (Grid Dimensions - Cố định theo vị trí) ---
    element_r_length: float = 0.0   # d_r (bề dày)
    element_t_length: float = 0.0   # arc_length (độ dài cung)
    element_z_length: float = 0.0   # d_z (chiều cao)

    # --- Kích thước kế thừa (Inherited Dimensions - Từ Segment) ---
    segment_r_length: float = 0.0
    segment_t_length: float = 0.0
    segment_z_length: float = 0.0

def extract_element_info(
    position: tuple, 
    geometry: Any, 
    mesh: Any, 
    sampling_density: int = 5  # <--- TĂNG MẬT ĐỘ (5^3 = 125 điểm/voxel)
) -> Optional[ElementInfo]:
    """
    Trích xuất thông tin phần tử tại vị trí (i, j, k) sử dụng phương pháp
    Bầu cử phân cấp (Hierarchical Voting) với đám mây điểm dày đặc.
    """

    # --- 1. CHUẨN BỊ DỮ LIỆU GRID & VALIDATION ---
    if not isinstance(position, (tuple, list)) or len(position) != 3:
        raise TypeError("Position phải là tuple (i_r, i_t, i_z)")

    i_r, i_t, i_z = position
    r_nodes, t_nodes, z_nodes = mesh.r_nodes, mesh.theta_nodes, mesh.z_nodes

    # Kiểm tra index hợp lệ
    if not (0 <= i_r < len(r_nodes) - 1): return None
    if not (0 <= i_t < len(t_nodes) - 1): return None
    if not (0 <= i_z < len(z_nodes) - 1): return None

    # Lấy tọa độ biên của Voxel
    r_i, r_next = float(r_nodes[i_r]), float(r_nodes[i_r+1])
    t_j, t_next = float(t_nodes[i_t]), float(t_nodes[i_t+1])
    z_k, z_next = float(z_nodes[i_z]), float(z_nodes[i_z+1])

    # Tính kích thước của Grid Element (Voxel)
    d_r = abs(r_next - r_i)
    d_t = abs(t_next - t_j)
    d_z = abs(z_next - z_k)
    r_avg = (r_i + r_next) / 2.0
    grid_arc_len = r_avg * d_t

    # --- 2. TẠO ĐÁM MÂY ĐIỂM (SUPER-SAMPLING) ---
    # EPSILON NHỎ HƠN ĐỂ SÁT BIÊN
    eps = 1e-9 
    
    # Tạo các điểm mẫu (linspaces)
    r_samples = np.linspace(r_i + eps*d_r, r_next - eps*d_r, sampling_density)
    t_samples = np.linspace(t_j + eps*d_t, t_next - eps*d_t, sampling_density)
    z_samples = np.linspace(z_k + eps*d_z, z_next - eps*d_z, sampling_density)
    
    # Meshgrid 3D
    R_grid, T_grid, Z_grid = np.meshgrid(r_samples, t_samples, z_samples, indexing='ij')
    
    # Chuyển đổi sang tọa độ Descartes (x, y, z) để check va chạm
    X_flat = (R_grid * np.cos(T_grid)).flatten()
    Y_flat = (R_grid * np.sin(T_grid)).flatten()
    Z_flat = Z_grid.flatten()
    
    sample_points = np.column_stack((X_flat, Y_flat, Z_flat))
    total_samples = sample_points.shape[0]
    voxel_center = np.mean(sample_points, axis=0).reshape(1,3)

    # --- 3. LOGIC BẦU CỬ (VOTING) ---
    segments_list = geometry.geometry if hasattr(geometry, 'geometry') else geometry

    segment_votes = {}              # Phiếu cho từng segment
    material_votes = defaultdict(int) # Phiếu tổng cho từng vật liệu
    total_hits = 0

    for seg in segments_list:
        if not hasattr(seg, 'mesh') or seg.mesh is None:
            continue
        
        # Check nhanh Bounding Box để tăng tốc
        if not seg.mesh.bounding_box.contains(voxel_center)[0]:
            # Nếu lưới rất mịn, check tâm là đủ. 
            # Nếu muốn an toàn tuyệt đối, có thể check overlap bounding box ở đây.
            continue
            
        # Kiểm tra chính xác: Điểm nào nằm trong Mesh?
        contained_mask = seg.mesh.contains(sample_points)
        vote_count = np.sum(contained_mask)
        
        if vote_count > 0:
            segment_votes[seg] = vote_count
            material_votes[seg.material] += vote_count
            total_hits += vote_count

    # Tính phiếu cho Không khí (Air)
    material_votes["air"] = total_samples - total_hits

    # --- 4. XÁC ĐỊNH NGƯỜI CHIẾN THẮNG ---
    
    # Bước A: Tìm Vật liệu chiếm ưu thế
    dominant_material = max(material_votes, key=material_votes.get)
    dominant_segment = None

    # Bước B: Tìm Segment chiếm ưu thế trong vật liệu đó
    if dominant_material != "air":
        max_seg_votes = -1
        for seg, votes in segment_votes.items():
            if seg.material == dominant_material:
                if votes > max_seg_votes:
                    max_seg_votes = votes
                    dominant_segment = seg

    # --- 5. HÀM HỖ TRỢ TRÍCH XUẤT ---
    def get_vec(obj, attr):
        val = getattr(obj, attr, None)
        return np.array(val, dtype=float) if val is not None else np.array([0., 0., 0.])

    def safe_float(obj, attr, default_val=0.0):
        val = getattr(obj, attr, None)
        return float(val) if val is not None else default_val

    # --- 6. TRẢ VỀ KẾT QUẢ ---

    # TRƯỜNG HỢP 1: KHÔNG KHÍ (Fallback)
    if dominant_segment is None:
        return ElementInfo(
            material="air",
            magnet_source=0.0,
            magnetization_direction=np.array([0., 0., 1.]),
            winding_vector=np.array([0., 0., 0.]),
            winding_normal=np.array([0., 0., 1.]),
            
            # Grid Dimensions
            element_r_length=float(d_r),
            element_t_length=float(grid_arc_len),
            element_z_length=float(d_z),
            
            # Inherited Dimensions (Fallback về Grid)
            segment_r_length=float(d_r),
            segment_t_length=float(grid_arc_len),
            segment_z_length=float(d_z)
        )

    # TRƯỜNG HỢP 2: CÓ SEGMENT CHIẾM ƯU THẾ
    # Lấy kích thước từ segment (nếu có), nếu không có thì fallback về grid dimensions
    seg_r = safe_float(dominant_segment, "r_length", d_r)
    seg_t = safe_float(dominant_segment, "t_length", grid_arc_len)
    seg_z = safe_float(dominant_segment, "z_length", d_z)

    return ElementInfo(
        material=dominant_segment.material,
        
        magnet_source=safe_float(dominant_segment, "magnet_source"),
        magnetization_direction=get_vec(dominant_segment, "magnetization_direction"),
        
        winding_vector=get_vec(dominant_segment, "winding_vector"),
        winding_normal=get_vec(dominant_segment, "winding_normal"),
        
        # Grid Dimensions (Luôn tính từ lưới)
        element_r_length=float(d_r),
        element_t_length=float(grid_arc_len),
        element_z_length=float(d_z),
        
        # Inherited Dimensions (Kế thừa từ segment thắng cử)
        segment_r_length=seg_r,
        segment_t_length=seg_t,
        segment_z_length=seg_z
    )
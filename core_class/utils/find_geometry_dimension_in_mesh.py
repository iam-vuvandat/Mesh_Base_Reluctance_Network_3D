import numpy as np
import trimesh
from tqdm import tqdm

def find_geometry_dimension_in_mesh(geometry, mesh):
    """
    Đo đạc kích thước r, t, z của các segment trong không gian lưới.
    Cập nhật trực tiếp thuộc tính: r_length, t_length, z_length.
    Nếu segment nằm hoàn toàn ngoài lưới, giữ giá trị là None.
    """
    
    # 1. Lấy danh sách segment
    segments = geometry.geometry if hasattr(geometry, 'geometry') else geometry
    
    # 2. Lấy dữ liệu lưới
    r_nodes = mesh.r_nodes
    t_nodes = mesh.theta_nodes
    z_nodes = mesh.z_nodes
    
    # Xác định phạm vi bao phủ của toàn bộ Grid
    grid_r_min, grid_r_max = r_nodes[0], r_nodes[-1]
    grid_z_min, grid_z_max = z_nodes[0], z_nodes[-1]
    
    print(f"[INFO] Measuring Segments within Mesh Grid...")
    
    count_out_of_bounds = 0
    count_fallback = 0
    
    for seg in tqdm(segments, desc="Processing"):
        # Reset hoặc khởi tạo giá trị mặc định là None (để đánh dấu chưa tính/không tính)
        seg.r_length = None
        seg.t_length = None
        seg.z_length = None
        
        if seg.mesh is None:
            continue
            
        # --- BƯỚC 1: KHOANH VÙNG & CHECK OUT-OF-BOUNDS ---
        # Lấy Bounding Box Descartes
        bbox_min, bbox_max = seg.mesh.bounds
        z_seg_min, z_seg_max = bbox_min[2], bbox_max[2]
        
        # Chuyển đổi BBox sang hệ trụ (ước lượng r)
        corners = trimesh.bounds.corners(seg.mesh.bounds)
        r_corners = np.sqrt(corners[:,0]**2 + corners[:,1]**2)
        r_seg_min, r_seg_max = np.min(r_corners), np.max(r_corners)
        
        # Kiểm tra nhanh: Segment có nằm hoàn toàn ngoài phạm vi R hoặc Z của lưới không?
        # Nếu R_seg_max < Grid_R_min (Nằm trong lỗ trục)
        # Hoặc R_seg_min > Grid_R_max (Nằm ngoài vỏ)
        # Hoặc Z_seg_max < Grid_Z_min (Nằm dưới đáy)
        # Hoặc Z_seg_min > Grid_Z_max (Nằm trên đỉnh)
        if (r_seg_max < grid_r_min or r_seg_min > grid_r_max or 
            z_seg_max < grid_z_min or z_seg_min > grid_z_max):
            
            count_out_of_bounds += 1
            # Không làm gì cả, giữ nguyên là None và skip qua segment này
            continue

        # --- BƯỚC 2: TÌM INDEX TRÊN GRID ---
        # Tìm index range (mở rộng biên +/- 1 để an toàn)
        i_r_start = max(0, np.searchsorted(r_nodes, r_seg_min) - 1)
        i_r_end   = min(len(r_nodes)-1, np.searchsorted(r_nodes, r_seg_max) + 1)
        
        i_z_start = max(0, np.searchsorted(z_nodes, z_seg_min) - 1)
        i_z_end   = min(len(z_nodes)-1, np.searchsorted(z_nodes, z_seg_max) + 1)
        
        # Theta quét toàn bộ (để an toàn)
        i_t_start, i_t_end = 0, len(t_nodes) - 1
        
        # Check lại lần nữa index (phòng hờ searchsorted trả về biên)
        if i_r_start >= i_r_end or i_z_start >= i_z_end:
            count_out_of_bounds += 1
            continue

        # --- BƯỚC 3: TẠO LƯỚI TÂM CỤC BỘ ---
        r_sub = r_nodes[i_r_start : i_r_end+1]
        t_sub = t_nodes[i_t_start : i_t_end+1]
        z_sub = z_nodes[i_z_start : i_z_end+1]
        
        r_c = (r_sub[:-1] + r_sub[1:]) / 2
        t_c = (t_sub[:-1] + t_sub[1:]) / 2
        z_c = (z_sub[:-1] + z_sub[1:]) / 2
        
        # Meshgrid 3D
        R_g, T_g, Z_g = np.meshgrid(r_c, t_c, z_c, indexing='ij')
        
        # Sang Descartes
        X_flat = (R_g * np.cos(T_g)).flatten()
        Y_flat = (R_g * np.sin(T_g)).flatten()
        Z_flat = Z_g.flatten()
        
        candidates = np.column_stack((X_flat, Y_flat, Z_flat))
        
        if len(candidates) == 0:
            count_out_of_bounds += 1
            continue

        # --- BƯỚC 4: KIỂM TRA VA CHẠM ---
        mask = seg.mesh.contains(candidates)
        
        # --- BƯỚC 5: TÍNH TOÁN KÍCH THƯỚC ---
        if np.any(mask):
            # == TRƯỜNG HỢP 1: CÓ VOXEL BỊ CHIẾM (LÝ TƯỞNG) ==
            mask_3d = mask.reshape(len(r_c), len(t_c), len(z_c))
            valid_r, valid_t, valid_z = np.where(mask_3d)
            
            # A. R Length
            min_r, max_r = np.min(valid_r), np.max(valid_r)
            seg.r_length = float(r_sub[max_r + 1] - r_sub[min_r])
            
            # B. Z Length
            min_z, max_z = np.min(valid_z), np.max(valid_z)
            seg.z_length = float(z_sub[max_z + 1] - z_sub[min_z])
            
            # C. T Length (Arc)
            min_t, max_t = np.min(valid_t), np.max(valid_t)
            opening_angle = t_sub[max_t + 1] - t_sub[min_t]
            
            # Bán kính trung bình của vùng bị chiếm
            r_occupied_avg = (r_sub[max_r + 1] + r_sub[min_r]) / 2.0
            seg.t_length = float(r_occupied_avg * opening_angle)
            
        else:
            # == TRƯỜNG HỢP 2: FALLBACK (SEGMENT QUÁ MỎNG) ==
            # Segment nằm trong phạm vi lưới nhưng không chứa tâm voxel nào.
            # Ta dùng chính Bounding Box của Segment để ước lượng.
            
            count_fallback += 1
            
            # Z fallback
            seg.z_length = float(z_seg_max - z_seg_min)
            
            # R fallback
            seg.r_length = float(r_seg_max - r_seg_min)
            
            # T fallback: Lấy kích thước của 1 ô lưới làm "kích thước tối thiểu"
            if len(r_c) > 0 and len(t_c) > 0:
                 dr_grid = r_sub[1] - r_sub[0]
                 dt_grid = t_sub[1] - t_sub[0]
                 
                 # Gán kích thước tối thiểu nếu kích thước BBox quá nhỏ
                 if seg.r_length < 1e-9: seg.r_length = float(dr_grid)
                 if seg.z_length < 1e-9: seg.z_length = float(z_sub[1]-z_sub[0])
                 
                 r_center_grid = (r_sub[0] + r_sub[-1])/2
                 seg.t_length = float(r_center_grid * dt_grid)

    if count_out_of_bounds > 0:
        print(f"[INFO] Skipped {count_out_of_bounds} segments completely out of mesh bounds.")
    if count_fallback > 0:
        print(f"[WARNING] Used fallback dimension for {count_fallback} segments (Mesh too coarse).")
    
    print("[INFO] Dimensions calculation completed.")
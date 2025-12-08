import numpy as np
import pyvista as pv

def show_reluctance_network(reluctance_network):
    """
    Hiển thị Mạng từ trở (Voxelized Geometry).
    Tách riêng các vật liệu để tùy chỉnh màu sắc và độ trong suốt.
    """
    
    # 1. Lấy dữ liệu
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    
    print("[VISUALIZATION] Generating Voxel Data...")

    # 2. Tạo Grid gốc từ Mesh
    grid_pv = mesh_obj.to_pyvista_grid()
    
    # 3. Tạo mảng ID vật liệu (Mapping)
    # 0: Air, 1: Iron, 2: Magnet, 3: Coil
    flat_elements = elements_matrix.flatten(order='F')
    
    mat_ids = np.zeros(len(flat_elements), dtype=int)
    
    for idx, el in enumerate(flat_elements):
        if el is None: continue
        mat_name = str(el.material).lower()
        
        if "iron" in mat_name or "steel" in mat_name: mat_ids[idx] = 1
        elif "magnet" in mat_name:                    mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name or "copper" in mat_name: mat_ids[idx] = 3
        else:                                         mat_ids[idx] = 0 # Air
    
    # Gán ID vào lưới tổng
    grid_pv.cell_data["MatID"] = mat_ids
    
    # 4. Khởi tạo Plotter
    pv.set_plot_theme("dark")
    pl = pv.Plotter(window_size=[1400, 1000])
    pl.set_background("#0F0F0F")
    pl.add_axes()
    pl.add_text("VOXELIZED MODEL (DISCRETIZED)", position='upper_right', font_size=12, color='white')

    # --- CẤU HÌNH HIỂN THỊ CHO TỪNG VẬT LIỆU ---
    # Format: ID: (Label, Color, Opacity)
    styles = {
        0: ("Air",    "white",  0.2),  # <--- Air: Trắng, mờ 20%
        1: ("Iron",   "gray",   1.0),  # <--- Iron: Xám, đặc
        2: ("Magnet", "red",    1.0),  # <--- Magnet: Đỏ, đặc
        3: ("Coil",   "orange", 1.0)   # Coil: Cam, đặc
    }

    print("[VISUALIZATION] Rendering layers...")

    # 5. Tách và Vẽ từng lớp vật liệu
    for mat_id, (label, color, opacity) in styles.items():
        
        # Lọc lấy các voxel thuộc vật liệu này
        # threshold trả về lưới con chỉ chứa các cell có giá trị trong khoảng [mat_id, mat_id]
        sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
        
        # Nếu có dữ liệu thì vẽ
        if sub_mesh.n_cells > 0:
            # Gán tên vật liệu vào mesh để dùng khi click
            sub_mesh.field_data["Label"] = [label] * sub_mesh.n_cells # Dữ liệu dummy để biết tên
            
            # Cấu hình viền (Edge color)
            # Nếu là Air thì viền nhạt cho đỡ rối, còn lại viền tối
            edge_color = "#AAAAAA" if mat_id == 0 else "#333333"
            
            pl.add_mesh(sub_mesh, 
                        color=color, 
                        opacity=opacity,
                        show_edges=True,
                        edge_color=edge_color,
                        lighting=True,
                        label=label) # Label cho legend

    # 6. Tương tác Click
    def on_pick(mesh):
        if mesh is None: return
        try:
            # Vì ta đã tách mesh, ta có thể biết ngay mesh nào được click dựa vào màu/tên
            # Nhưng pyvista trả về một mesh con cục bộ tại điểm click.
            # Cách đơn giản nhất là dựa vào màu hoặc check field data nếu gán trước đó.
            
            # Ở đây ta check ID vật liệu trong mesh được trả về
            if "MatID" in mesh.cell_data:
                mid = mesh.cell_data["MatID"][0]
                name = styles[mid][0]
                
                # Hiển thị thông báo
                pl.add_text(f"SELECTED VOXEL: {name}", position='upper_left', 
                            font_size=12, color='yellow', name='hud')
        except: pass

    pl.enable_mesh_picking(on_pick, show_message=False, show=False)

    # Thêm chú thích (Legend)
    pl.add_legend(bcolor=(0.1, 0.1, 0.1), border=True, size=(0.15, 0.15))
    
    # Góc nhìn Isometric
    pl.view_isometric()
    pl.show()
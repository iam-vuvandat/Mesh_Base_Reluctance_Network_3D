import numpy as np
import pyvista as pv

def show_reluctance_network(reluctance_network):
    """
    Hiển thị Mạng từ trở (Phiên bản Custom Keys - Fix Font Error).
    Phím tắt:
      - i/o : Di chuyển Bán kính (Radial - i)
      - l/r : Di chuyển Góc (Tangential - j)
      - u/d : Di chuyển Trục (Axial - z)
    """
    
    # --- 1. CHUẨN BỊ DỮ LIỆU ---
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    
    # Lấy kích thước lưới (nr=i, nt=j, nz=z)
    nr, nt, nz = elements_matrix.shape
    
    print("[VISUALIZATION] Generating Voxel Data...")
    grid_pv = mesh_obj.to_pyvista_grid()
    
    # Flatten dữ liệu theo thứ tự Fortran
    flat_elements = elements_matrix.flatten(order='F')
    
    # Gán ID gốc để pick chính xác
    grid_pv.cell_data["OrigID"] = np.arange(grid_pv.n_cells)
    
    # Tạo ID vật liệu
    mat_ids = np.zeros(len(flat_elements), dtype=int)
    for idx, el in enumerate(flat_elements):
        if el is None: continue
        mat_name = str(el.material).lower()
        if "iron" in mat_name or "steel" in mat_name: mat_ids[idx] = 1
        elif "magnet" in mat_name:                    mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name: mat_ids[idx] = 3
        else:                                         mat_ids[idx] = 0 # Air
    
    grid_pv.cell_data["MatID"] = mat_ids

    # --- 2. KHỞI TẠO PLOTTER ---
    pv.set_plot_theme("dark")
    pl = pv.Plotter(window_size=[1400, 1000])
    pl.set_background("#0F0F0F")
    pl.add_axes()
    
    # Cập nhật hướng dẫn phím bấm trên màn hình
    instructions = (
        "NAVIGATION MODE\n"
        "----------------\n"
        "Click : Select Element\n"
        "i / o : Radius (In/Out)\n"
        "l / r : Theta  (Left/Right)\n"
        "u / d : Z-Axis (Up/Down)"
    )
    # SỬA LỖI: Dùng 'font' thay vì 'font_family'
    pl.add_text(instructions, position='upper_right', font_size=10, color='white', font='courier')

    # --- 3. VẼ CÁC LỚP VẬT LIỆU ---
    styles = {
        0: ("Air",    "white",  0.1), 
        1: ("Iron",   "gray",   1.0),
        2: ("Magnet", "red",    1.0),
        3: ("Coil",   "orange", 1.0)
    }

    for mat_id, (label, color, opacity) in styles.items():
        sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
        if sub_mesh.n_cells > 0:
            edge_color = "#444444" if mat_id == 0 else "#222222"
            pl.add_mesh(sub_mesh, color=color, opacity=opacity, 
                        show_edges=True, edge_color=edge_color, label=label,
                        pickable=True)

    # --- 4. LOGIC TRẠNG THÁI (STATE) ---
    class ViewerState:
        def __init__(self):
            self.selected_idx = None # Tuple (ir, it, iz)
            self.highlight_actor = None 

        def update_selection(self, ir, it, iz):
            # Kiểm tra biên (Boundary Check)
            if not (0 <= ir < nr and 0 <= it < nt and 0 <= iz < nz): 
                return # Ra ngoài lưới thì không làm gì

            self.selected_idx = (ir, it, iz)
            
            # Tính Flat ID
            flat_id = ir + it * nr + iz * (nr * nt)
            
            # --- HIGHLIGHT (Làm sáng) ---
            if self.highlight_actor:
                pl.remove_actor(self.highlight_actor)
            
            try:
                cell_geo = grid_pv.extract_cells([flat_id])
                # Vẽ khung dây màu vàng sáng
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='yellow', 
                                                   line_width=5, render=False, name="highlight")
            except: pass

            # --- HIỂN THỊ THÔNG TIN ---
            element_obj = elements_matrix[ir, it, iz]
            
            # Header thông tin tọa độ
            info_str = f"INDEX: [i={ir}, j={it}, z={iz}]\n"
            info_str += f"Global ID: {flat_id}\n"
            
            if element_obj is None:
                info_str += "Status: Empty Element"
            else:
                info_str += "="*25 + "\n"
                attrs = vars(element_obj)
                for key, val in attrs.items():
                    if isinstance(val, float): info_str += f"{key}: {val:.4e}\n"
                    elif key in ['mesh', 'motor', 'geometry']: info_str += f"{key}: <Ref>\n"
                    else: info_str += f"{key}: {val}\n"

            # SỬA LỖI: Dùng 'font' thay vì 'font_family'
            pl.add_text(info_str, position='upper_left', font_size=12, 
                        color='yellow', font='courier', name='hud_info')
            pl.render()

    state = ViewerState()

    # --- 5. CLICK CHUỘT ---
    def on_cell_picked(picked_mesh):
        if picked_mesh is None or picked_mesh.n_cells == 0: return
        if "OrigID" in picked_mesh.cell_data:
            original_id = picked_mesh.cell_data["OrigID"][0]
            # Convert ID -> (ir, it, iz)
            iz = original_id // (nr * nt)
            rem = original_id % (nr * nt)
            it = rem // nr
            ir = rem % nr
            state.update_selection(ir, it, iz)

    pl.enable_cell_picking(mesh=None, callback=on_cell_picked, show=False, show_message=False, through=False)

    # --- 6. CÀI ĐẶT PHÍM BẤM (KEY BINDINGS) ---
    def move_cursor(dr, dt, dz):
        # Nếu chưa chọn gì thì bắt đầu từ (0,0,0)
        if state.selected_idx is None:
            state.update_selection(0, 0, 0)
        else:
            r, t, z = state.selected_idx
            state.update_selection(r + dr, t + dt, z + dz)

    # Phím điều hướng bán kính (Radial - i)
    pl.add_key_event("o", lambda: move_cursor(1, 0, 0))   # o: i+1 (Out)
    pl.add_key_event("i", lambda: move_cursor(-1, 0, 0))  # i: i-1 (In)

    # Phím điều hướng góc (Tangential - j)
    pl.add_key_event("r", lambda: move_cursor(0, 1, 0))   # r: j+1 (Right)
    pl.add_key_event("l", lambda: move_cursor(0, -1, 0))  # l: j-1 (Left)

    # Phím điều hướng trục (Axial - z)
    pl.add_key_event("u", lambda: move_cursor(0, 0, 1))   # u: z+1 (Up)
    pl.add_key_event("d", lambda: move_cursor(0, 0, -1))  # d: z-1 (Down)

    # --- 7. HIỂN THỊ ---
    pl.add_legend(bcolor=(0.1, 0.1, 0.1), border=True, size=(0.15, 0.15))
    pl.view_isometric()
    pl.show()
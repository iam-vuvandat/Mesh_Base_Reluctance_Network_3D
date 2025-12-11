import numpy as np
import pyvista as pv
import ctypes 

# --- 1. FIX LỖI MỜ (HIGH-DPI SCALING) ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

def show_reluctance_network(reluctance_network):
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    
    nr, nt, nz = elements_matrix.shape
    
    grid_pv = mesh_obj.to_pyvista_grid()
    flat_elements = elements_matrix.flatten(order='F')
    grid_pv.cell_data["OrigID"] = np.arange(grid_pv.n_cells)
    
    mat_ids = np.zeros(len(flat_elements), dtype=int)
    for idx, el in enumerate(flat_elements):
        if el is None: continue
        mat_name = str(el.material).lower()
        if "iron" in mat_name or "steel" in mat_name: mat_ids[idx] = 1
        elif "magnet" in mat_name:                    mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name: mat_ids[idx] = 3
        else:                                         mat_ids[idx] = 0
    
    grid_pv.cell_data["MatID"] = mat_ids

    pv.set_plot_theme("dark")
    pl = pv.Plotter(window_size=[2560, 1440]) 
    pl.set_background("#050505") 
    pl.add_axes()
    
    try:
        pl.enable_anti_aliasing('msaa', multi_samples=8)
    except: pass

    styles = {
        0: ("Air",    "#333333", 0.4), 
        1: ("Iron",   "#F0F0F0", 0.9), 
        2: ("Magnet", "#FF3333", 0.9), 
        3: ("Coil",   "#FFAA00", 0.9)  
    }

    # Nét mảnh 1.0 cho tinh tế
    line_w = 1.0 

    for mat_id, (label, color, opacity) in styles.items():
        sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
        if sub_mesh.n_cells > 0:
            pl.add_mesh(sub_mesh, 
                        style='wireframe',  # Chỉ vẽ khung dây (Rỗng ruột)
                        color=color, 
                        label=label,
                        pickable=True, 
                        line_width=line_w)

    pl.add_legend(bcolor='#1A1A1A', border=True, size=(0.15, 0.15), loc='lower right', face='rectangle')

    class ViewerState:
        def __init__(self):
            self.selected_idx = (0, 0, 0)
            self.highlight_actor = None 
            self.info_actor = None 
            self.show_text = True 

        def update_view(self, ir, it, iz):
            # Giới hạn chỉ số (Clamping)
            ir = int(np.clip(ir, 0, nr - 1))
            it = int(np.clip(it, 0, nt - 1))
            iz = int(np.clip(iz, 0, nz - 1))
            
            self.selected_idx = (ir, it, iz)
            flat_id = ir + it * nr + iz * (nr * nt)

            # Vẽ highlight (Khung dây màu Cyan sáng)
            if self.highlight_actor:
                pl.remove_actor(self.highlight_actor)
            try:
                cell_geo = grid_pv.extract_cells([flat_id])
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='#00FFFF', 
                                                    line_width=4, render=False, name="highlight")
            except: pass

            # Cập nhật Text thông tin
            if self.info_actor:
                pl.remove_actor(self.info_actor)

            if not self.show_text:
                pl.render()
                return

            element_obj = elements_matrix[ir, it, iz]
            
            info_str = f"VOXEL: [{ir}, {it}, {iz}]\n" + "-"*20 + "\n"
            
            if element_obj is None:
                info_str += "Status: Empty"
            else:
                attrs = vars(element_obj)
                for key, val in attrs.items():
                    if key == "dimension" and isinstance(val, np.ndarray):
                        info_str += "Dimension [r, t, z]:\n"
                        info_str += f" El: {val[0,:]}\n"
                    elif isinstance(val, float): 
                        info_str += f"{key}: {val:.6f}"
                    elif isinstance(val, np.ndarray):
                        with np.printoptions(formatter={'float': '{: 0.6f}'.format}):
                            arr_str = np.array2string(val.flatten(), separator=', ')
                        info_str += f"{key}:\n{arr_str}"
                    elif key in ['mesh', 'motor', 'geometry']: 
                        info_str += f"{key}: <Ref>"
                    else: 
                        info_str += f"{key}: {val}"
                    info_str += "\n"
            
            self.info_actor = pl.add_text(info_str, position='upper_left', font_size=16, 
                                        color='white', font='courier', name='hud_info')
            pl.render()

    state = ViewerState()
    state.update_view(0, 0, 0)

    # --- HÀM ĐIỀU KHIỂN ---
    def move_r(val): 
        r, t, z = state.selected_idx
        state.update_view(r + (1 if val else -1), t, z)
    
    def move_t(val): 
        r, t, z = state.selected_idx
        state.update_view(r, t + (1 if val else -1), z)
    
    def move_z(val): 
        r, t, z = state.selected_idx
        state.update_view(r, t, z + (1 if val else -1))

    # --- TẠO 6 NÚT BẤM (GÓC TRÊN PHẢI) ---
    size = 35         # Kích thước nút
    x_base = 0.92     # Tọa độ cột phải (Nút +)
    x_prev = 0.88     # Tọa độ cột trái (Nút -)
    y_start = 0.90    # Tọa độ dòng đầu tiên
    y_step = 0.06     # Khoảng cách giữa các dòng

    # 1. Hàng AXIAL (Z) - Trên cùng
    pl.add_text("Z", position=(x_prev - 0.03, y_start), color='white', font_size=12)
    pl.add_checkbox_button_widget(lambda v: move_z(True),  position=(x_base, y_start), value=False, color_on='green', color_off='green', size=size)
    pl.add_checkbox_button_widget(lambda v: move_z(False), position=(x_prev, y_start), value=False, color_on='red',   color_off='red',   size=size)

    # 2. Hàng THETA (T) - Giữa
    pl.add_text("T", position=(x_prev - 0.03, y_start - y_step), color='white', font_size=12)
    pl.add_checkbox_button_widget(lambda v: move_t(True),  position=(x_base, y_start - y_step), value=False, color_on='green', color_off='green', size=size)
    pl.add_checkbox_button_widget(lambda v: move_t(False), position=(x_prev, y_start - y_step), value=False, color_on='red',   color_off='red',   size=size)

    # 3. Hàng RADIAL (R) - Dưới
    pl.add_text("R", position=(x_prev - 0.03, y_start - 2*y_step), color='white', font_size=12)
    pl.add_checkbox_button_widget(lambda v: move_r(True),  position=(x_base, y_start - 2*y_step), value=False, color_on='green', color_off='green', size=size)
    pl.add_checkbox_button_widget(lambda v: move_r(False), position=(x_prev, y_start - 2*y_step), value=False, color_on='red',   color_off='red',   size=size)

    # Vẫn giữ click chuột để tiện lợi
    def on_cell_picked(picked_mesh):
        if picked_mesh is None: return
        if isinstance(picked_mesh, pv.MultiBlock):
            if len(picked_mesh) == 0: return
            picked_mesh = picked_mesh[0]
        if not hasattr(picked_mesh, 'n_cells') or picked_mesh.n_cells == 0: return
        if "OrigID" in picked_mesh.cell_data:
            original_id = picked_mesh.cell_data["OrigID"][0]
            iz = original_id // (nr * nt)
            rem = original_id % (nr * nt)
            it = rem // nr
            ir = rem % nr
            state.update_view(ir, it, iz)

    pl.enable_cell_picking(mesh=None, callback=on_cell_picked, show=False, show_message=False, through=False, use_hardware=False)

    pl.view_isometric()
    pl.show()